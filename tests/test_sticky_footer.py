from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


STYLESHEETS = (
    REPO_ROOT / "tailwind.css",
    REPO_ROOT / "ckanext/cwbi_theme/assets/cwbi-theme.css",
)


TEMPLATE_BACKDROPS = {
    REPO_ROOT / "ckanext/cwbi_theme/templates/home/index.html":
        "cwbi-home-backdrop",
    REPO_ROOT / "ckanext/cwbi_theme/templates/cwbi_theme/landing.html":
        "cwbi-page-backdrop",
}


class StickyFooterStylesTests(unittest.TestCase):
    def test_custom_page_templates_restore_ckan_main_wrapper(self):
        for template, backdrop_class in TEMPLATE_BACKDROPS.items():
            content = template.read_text(encoding="utf-8")
            self.assertRegex(
                content,
                r'<div\s+class="main">\s*<div\s+class="{}"'.format(
                    backdrop_class
                ),
                str(template.relative_to(REPO_ROOT)),
            )

    def test_sticky_footer_layout_is_present_in_source_and_generated_css(self):
        for stylesheet in STYLESHEETS:
            content = stylesheet.read_text(encoding="utf-8")
            label = str(stylesheet.relative_to(REPO_ROOT))

            self.assertRegex(
                content,
                r"html,\s*body\s*\{[^}]*min-height:\s*100%;",
                label,
            )
            self.assertRegex(
                content,
                r"body\s*\{[^}]*min-height:\s*100vh;[^}]*display:\s*flex;"
                r"[^}]*flex-direction:\s*column;",
                label,
            )
            self.assertRegex(
                content,
                r"body\s*>\s*\.main\s*\{[^}]*flex:\s*1 0 auto;",
                label,
            )
            self.assertRegex(
                content,
                r"\.site-footer\s*\{[^}]*flex-shrink:\s*0;",
                label,
            )


if __name__ == "__main__":
    unittest.main()
