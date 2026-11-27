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
    REPO_ROOT / "ckanext/cwbi_theme/templates/package/search.html":
        "cwbi-page-backdrop cwbi-dataset-backdrop",
}


class StickyFooterStylesTests(unittest.TestCase):
    def test_home_cards_are_not_navigation_links(self):
        content = (
            REPO_ROOT / "ckanext/cwbi_theme/templates/home/index.html"
        ).read_text(encoding="utf-8")
        cards = re.search(
            r'<section class="cwbi-cards-section">(?P<body>.*?)</section>',
            content,
            re.DOTALL,
        )
        self.assertIsNotNone(cards)
        card_content = cards.group("body")
        self.assertEqual(6, card_content.count('<div class="cwbi-card">'))
        self.assertNotRegex(card_content, r"<a\b")
        self.assertNotIn("href=", card_content)

    def test_footer_exposes_cwbi_navigation_and_static_logo(self):
        content = (
            REPO_ROOT / "ckanext/cwbi_theme/templates/footer.html"
        ).read_text(encoding="utf-8")
        self.assertIn("{% block footer_content %}", content)
        self.assertIn("h.url_for_static('CWBI_Logo.png')", content)
        self.assertIn('class="h-16 w-16 mx-auto lg:mx-0"', content)
        self.assertNotIn("xl:max-h-96", content)
        self.assertIn("list-none space-y-0 leading-tight", content)
        self.assertNotIn("mt-10", content)
        self.assertIn("lg:items-start", content)
        self.assertEqual(3, content.count('class="mt-4 lg:!mt-0"'))
        heading_classes = re.findall(r'<h3 class="([^"]+)"', content)
        self.assertEqual(3, len(heading_classes))
        self.assertEqual(1, len(set(heading_classes)))
        for label in (
            "CWBI Program",
            "Communications",
            "Technical Resources",
            "About CWBI",
            "CWBI Modules",
            "Situation Reports",
            "Developer Documentation",
            "GitHub Enterprise",
        ):
            self.assertIn(label, content)

    def test_custom_page_templates_restore_ckan_main_wrapper(self):
        for template, backdrop_class in TEMPLATE_BACKDROPS.items():
            content = template.read_text(encoding="utf-8")
            content_block = re.search(
                r"{% block content %}(?P<body>.*?){% endblock %}",
                content,
                re.DOTALL,
            )
            self.assertIsNotNone(content_block, str(template.relative_to(REPO_ROOT)))
            self.assertRegex(
                content_block.group("body"),
                r'<div\s+class="main cwbi-full-page-main">\s*<div\s+class="{}"'.format(
                    backdrop_class
                ),
                str(template.relative_to(REPO_ROOT)),
            )
            self.assertRegex(
                content_block.group("body"),
                r"</div>\s*</div>\s*$",
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

    def test_backdrop_growth_and_dataset_background_contract_is_present(self):
        source = (REPO_ROOT / "tailwind.css").read_text(encoding="utf-8")
        self.assertRegex(
            source,
            r"\.cwbi-full-page-main\s*\{[^}]*@apply\s+flex\s+flex-col;",
        )
        self.assertRegex(
            source,
            r"\.cwbi-full-page-main\s*>\s*\.cwbi-home-backdrop,\s*"
            r"\.cwbi-full-page-main\s*>\s*\.cwbi-page-backdrop\s*\{"
            r"[^}]*flex:\s*1 0 auto;",
        )
        self.assertRegex(
            source,
            r"\.cwbi-dataset-backdrop\s*\{[^}]*"
            r"background-repeat:\s*no-repeat;[^}]*"
            r"background-size:\s*100% auto;",
        )

        generated = (
            REPO_ROOT / "ckanext/cwbi_theme/assets/cwbi-theme.css"
        ).read_text(encoding="utf-8")
        self.assertRegex(
            generated,
            r"\.cwbi-full-page-main\s*\{[^}]*display:\s*flex;[^}]*"
            r"flex-direction:\s*column;",
        )
        self.assertRegex(
            generated,
            r"\.cwbi-dataset-backdrop\s*\{[^}]*"
            r"background-repeat:\s*no-repeat;[^}]*"
            r"background-size:\s*100% auto;",
        )


if __name__ == "__main__":
    unittest.main()
