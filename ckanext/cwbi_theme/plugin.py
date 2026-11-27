import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint, redirect, request


LANDING_PAGES = {
    "discovery": {
        "title": "Data Discovery",
        "description": (
            "Find and access relevant data assets across CWBI modules to "
            "support operational decision-making."
        ),
        "banner": "Header_DataDiscovery.jpg",
    },
    "visibility": {
        "title": "Visibility",
        "description": (
            "Discover documented data sources through a centralized Civil "
            "Works data catalog."
        ),
        "banner": "Header_Visibility.jpg",
    },
    "vaultis": {
        "title": "VAULTIS Framework",
        "description": (
            "Support the Visibility and Accessibility principles of the "
            "VAULTIS framework through systematic data organization."
        ),
        "banner": "Header_VAULTISFramework.jpg",
    },
    "business-lines": {
        "title": "Business Lines",
        "description": "Explore data assets supporting Civil Works business lines.",
        "banner": "Header_BusinessLines.jpg",
    },
}


@toolkit.chained_helper
def humanize_entity_type(next_helper, entity_type, object_type, purpose):
    if entity_type == "organization":
        labels = {
            "default label": toolkit._("Module"),
            "no label": toolkit._("No Module"),
            "add link": toolkit._("Add Module"),
            "facet label": toolkit._("Modules"),
            "search placeholder": toolkit._("Search modules..."),
            "no description": toolkit._(
                "There is no description for this Module"
            ),
        }
        return labels.get(purpose, toolkit._("Modules"))
    return next_helper(entity_type, object_type, purpose)


@toolkit.chained_helper
def url_for(next_helper, *args, **kwargs):
    args, kwargs = _use_module_endpoint(args, kwargs)
    return next_helper(*args, **kwargs)


def _module_endpoint(endpoint):
    if isinstance(endpoint, str) and endpoint.startswith("organization."):
        return "cwbi_theme_modules." + endpoint.split(".", 1)[1]
    return endpoint


def _use_module_endpoint(args, kwargs):
    endpoint = args[0] if args else kwargs.get("endpoint")
    module_endpoint = _module_endpoint(endpoint)
    if module_endpoint != endpoint:
        if args:
            args = (module_endpoint, *args[1:])
        else:
            kwargs["endpoint"] = module_endpoint
    return args, kwargs


@toolkit.chained_helper
def build_nav_main(next_helper, *args):
    nav_items = []
    for item in args:
        if item and isinstance(item[0], str):
            item, _ = _use_module_endpoint(item, {})
        nav_items.append(item)
    return next_helper(*nav_items)


@toolkit.chained_helper
def build_nav(next_helper, *args, **kwargs):
    args, kwargs = _use_module_endpoint(args, kwargs)
    return next_helper(*args, **kwargs)


@toolkit.chained_helper
def build_nav_icon(next_helper, *args, **kwargs):
    args, kwargs = _use_module_endpoint(args, kwargs)
    return next_helper(*args, **kwargs)


@toolkit.chained_helper
def nav_link(next_helper, *args, **kwargs):
    if "named_route" in kwargs:
        kwargs["named_route"] = _module_endpoint(kwargs["named_route"])
    return next_helper(*args, **kwargs)


def group_create(context, data_dict=None):
    user = context.get("auth_user_obj")
    if user and user.sysadmin:
        return {"success": True}
    return {
        "success": False,
        "msg": toolkit._("Only sysadmins can create groups"),
    }


blueprint = Blueprint("cwbi_theme", __name__)


@blueprint.before_app_request
def redirect_organization_routes():
    script_root = request.script_root.rstrip("/")
    route_path = request.path
    if script_root and route_path.startswith(script_root + "/"):
        route_path = route_path[len(script_root) :]
    if route_path != "/organization" and not route_path.startswith(
        "/organization/"
    ):
        return None

    module_index_url = toolkit.url_for("cwbi_theme_modules.index")
    target = module_index_url.rstrip("/") + route_path[len("/organization") :]
    if request.query_string:
        target += "?" + request.query_string.decode("latin-1")
    return redirect(target, code=308)


def _render_landing_page(page_name):
    return toolkit.render(
        "cwbi_theme/landing.html",
        extra_vars={"landing_page": LANDING_PAGES[page_name]},
    )


@blueprint.route("/discovery")
def discovery():
    return _render_landing_page("discovery")


@blueprint.route("/visibility")
def visibility():
    return _render_landing_page("visibility")


@blueprint.route("/vaultis")
def vaultis():
    return _render_landing_page("vaultis")


@blueprint.route("/business-lines")
def business_lines():
    return _render_landing_page("business-lines")


class CwbiThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "public")
        toolkit.add_resource("assets", "cwbi_theme")

    def get_blueprint(self):
        from ckan.views.group import register_group_plugin_rules

        modules_blueprint = Blueprint(
            "cwbi_theme_modules",
            __name__,
            url_prefix="/modules",
            url_defaults={
                "group_type": "organization",
                "is_organization": True,
            },
        )
        register_group_plugin_rules(modules_blueprint)
        return [blueprint, modules_blueprint]

    def get_helpers(self):
        return {
            "humanize_entity_type": humanize_entity_type,
            "url_for": url_for,
            "build_nav_main": build_nav_main,
            "build_nav": build_nav,
            "build_nav_icon": build_nav_icon,
            "nav_link": nav_link,
        }

    def get_auth_functions(self):
        return {"group_create": group_create}
