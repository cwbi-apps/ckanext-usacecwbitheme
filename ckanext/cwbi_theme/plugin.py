import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint


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
    "modules": {
        "title": "Modules",
        "description": "Explore data assets contributed by CWBI modules.",
        "banner": "Header_Modules.jpg",
    },
}


blueprint = Blueprint("cwbi_theme", __name__)


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


@blueprint.route("/modules")
def modules():
    return _render_landing_page("modules")


class CwbiThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "public")
        toolkit.add_resource("assets", "cwbi_theme")

    def get_blueprint(self):
        return blueprint
