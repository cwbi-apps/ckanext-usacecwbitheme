import os
import re
import unittest
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import urlopen


BASE_URL = os.environ.get("CKAN_LIVE_BASE_URL")
REQUEST_TIMEOUT_SECONDS = 20


class LiveCkanTemplateRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not BASE_URL:
            raise RuntimeError(
                "Set CKAN_LIVE_BASE_URL to the base URL of a running CKAN site."
            )
        cls.base_url = BASE_URL.rstrip("/") + "/"

    def render_page(self, path):
        url = urljoin(self.base_url, path)
        try:
            with urlopen(url, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                self.assertEqual(200, response.status, url)
                self.assertIn("text/html", response.headers.get("Content-Type", ""))
                return response.read().decode("utf-8", errors="replace")
        except HTTPError as error:
            self.fail("CKAN returned HTTP {} for {}".format(error.code, url))
        except URLError as error:
            self.fail("Could not reach CKAN at {}: {}".format(url, error.reason))

    def test_module_index_renders_module_labels(self):
        html = self.render_page("modules/")
        self.assertIn("What are Modules?", html)
        self.assertIn("Search modules...", html)
        self.assertNotIn("Organizations", html)
        self.assertIn('href="/modules/"', html)
        self.assertNotIn('href="/organization/', html)

    def test_organization_index_redirects_to_modules(self):
        url = urljoin(self.base_url, "organization/")
        with urlopen(url, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            self.assertEqual(
                urljoin(self.base_url, "modules/"),
                response.geturl(),
            )
            self.assertIn("What are Modules?", response.read().decode(
                "utf-8", errors="replace"
            ))

    def test_dataset_search_renders_module_labels(self):
        html = self.render_page("dataset/")
        self.assertIn("Modules", html)
        self.assertNotIn("Organizations", html)
        self.assertIn('href="/modules/"', html)
        self.assertNotIn('href="/organization/', html)

    def test_homepage_cards_render_without_links(self):
        html = self.render_page("")
        cards = re.search(
            r'<section class="cwbi-cards-section">(?P<body>.*?)</section>',
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(cards)
        card_content = cards.group("body")
        self.assertEqual(6, card_content.count('<div class="cwbi-card">'))
        self.assertNotRegex(card_content, r"<a\b")

    def test_footer_renders_cwbi_navigation_and_logo(self):
        html = self.render_page("")
        self.assertIn('alt="CWBI"', html)
        self.assertRegex(html, r'src="[^"]*CWBI_Logo\.png"')
        for label in (
            "CWBI Program",
            "Communications",
            "Technical Resources",
            "About CWBI",
            "CWBI Modules",
            "Cyber Security",
            "Situation Reports",
            "Infrastructure Priorities",
            "Developer Documentation",
            "Data Load Documentation",
            "Confluence Program Documentation",
            "GitHub Enterprise",
        ):
            self.assertIn(label, html)
        self.assertIn('href="/modules"', html)


if __name__ == "__main__":
    unittest.main()
