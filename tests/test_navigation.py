from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
HEADER_TEMPLATE = REPO_ROOT / "ckanext/cwbi_theme/templates/header.html"
ORGANIZATION_TEMPLATE = (
    REPO_ROOT / "ckanext/cwbi_theme/templates/organization/index.html"
)
PACKAGE_CREATE_TEMPLATE = (
    REPO_ROOT
    / "ckanext/cwbi_theme/templates/package/snippets/cannot_create_package.html"
)
PLUGIN = REPO_ROOT / "ckanext/cwbi_theme/plugin.py"


class NavigationTests(unittest.TestCase):
    def test_organization_navigation_is_labeled_modules(self):
        content = HEADER_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("_('Modules')", content)
        self.assertNotIn("_('Organizations')", content)

    def test_group_navigation_requires_group_creation_access(self):
        content = HEADER_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("h.check_access('group_create')", content)
        self.assertIn(
            "build_nav_main(dataset_tab, modules_tab, groups_tab",
            content,
        )
        self.assertIn("build_nav_main(dataset_tab, modules_tab, about_tab)", content)

        plugin = PLUGIN.read_text(encoding="utf-8")
        self.assertIn("plugins.implements(plugins.IAuthFunctions)", plugin)
        self.assertIn('"group_create": group_create', plugin)
        self.assertIn("user and user.sysadmin", plugin)

    def test_organization_index_uses_module_labels_and_search_results(self):
        content = ORGANIZATION_TEMPLATE.read_text(encoding="utf-8")
        for label in (
            "What are Modules?",
            "Search modules...",
            "type='module'",
            "There are currently no Modules for this site",
            "Add Module",
        ):
            self.assertIn(label, content)
        self.assertNotIn("Organizations", content)
        self.assertNotIn("organization found", content)

    def test_ckan_dataset_labels_use_module_terminology(self):
        plugin = PLUGIN.read_text(encoding="utf-8")
        self.assertIn("@toolkit.chained_helper", plugin)
        self.assertIn('if entity_type == "organization":', plugin)
        self.assertIn('"facet label": toolkit._("Modules")', plugin)
        self.assertIn('"default label": toolkit._("Module")', plugin)
        self.assertIn('"no label": toolkit._("No Module")', plugin)
        self.assertIn('"add link": toolkit._("Add Module")', plugin)
        self.assertIn('"no description": toolkit._(', plugin)
        self.assertIn("There is no description for this Module", plugin)
        self.assertIn('"humanize_entity_type": humanize_entity_type', plugin)

        content = PACKAGE_CREATE_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("create a Module", content)
        self.assertIn("There are no Modules", content)
        translated_text = " ".join(re.findall(r"_\('([^']*)'\)", content))
        self.assertNotIn("organization", translated_text.lower())

    def test_organization_routes_are_exposed_as_modules(self):
        plugin = PLUGIN.read_text(encoding="utf-8")
        self.assertIn('url_prefix="/modules"', plugin)
        self.assertIn('"group_type": "organization"', plugin)
        self.assertIn('"is_organization": True', plugin)
        self.assertIn('startswith("organization.")', plugin)
        self.assertIn(
            'toolkit.url_for("cwbi_theme_modules.index")',
            plugin,
        )
        self.assertIn('return redirect(target, code=308)', plugin)
        self.assertIn('def build_nav_main(next_helper, *args):', plugin)
        self.assertIn('"build_nav": build_nav', plugin)
        self.assertIn('"nav_link": nav_link', plugin)


if __name__ == "__main__":
    unittest.main()
