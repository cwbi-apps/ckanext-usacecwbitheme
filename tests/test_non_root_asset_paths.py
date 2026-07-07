from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


THEME_PUBLIC_ASSET_PATTERNS = (
    "CWBI_",
    "Header_",
    "Homepage_",
    "favicon-",
)


SOURCE_FILES = (
    REPO_ROOT / "ckanext/cwbi_theme/templates/base.html",
    REPO_ROOT / "ckanext/cwbi_theme/templates/header.html",
    REPO_ROOT / "ckanext/cwbi_theme/templates/home/index.html",
    REPO_ROOT / "ckanext/cwbi_theme/templates/package/search.html",
    REPO_ROOT / "ckanext/cwbi_theme/templates/cwbi_theme/landing.html",
    REPO_ROOT / "tailwind.css",
    REPO_ROOT / "ckanext/cwbi_theme/assets/cwbi-theme.css",
)


URL_REFERENCE_RE = re.compile(
    r"""
    (?:
        \b(?:href|src)=["'](?P<html>[^"']+)["']
        |
        url\(["']?(?P<css>[^"')]+)["']?\)
        |
        url_for_static\(["'](?P<static>[^"']+)["']
    )
    """,
    re.VERBOSE,
)


def is_theme_public_asset(reference):
    basename = Path(reference.split("?", 1)[0].split("#", 1)[0]).name
    return any(basename.startswith(prefix) for prefix in THEME_PUBLIC_ASSET_PATTERNS)


def references_in(path):
    text = path.read_text(encoding="utf-8")
    for match in URL_REFERENCE_RE.finditer(text):
        yield match.group("html") or match.group("css") or match.group("static")


class NonRootAssetPathTests(unittest.TestCase):
    def test_theme_source_does_not_hardcode_root_public_asset_paths(self):
        offenders = []

        for source_file in SOURCE_FILES:
            self.assertTrue(source_file.exists(), "{} must exist".format(source_file))
            for reference in references_in(source_file):
                if reference.startswith("/") and is_theme_public_asset(reference):
                    offenders.append(
                        "- {}: {}".format(source_file.relative_to(REPO_ROOT), reference)
                    )

        if offenders:
            self.fail(
                "\n".join(
                    [
                        "Theme source hardcodes root-relative public asset paths.",
                        "",
                        "When CKAN is deployed below a path such as /catalog, "
                        "these references bypass that deployment path:",
                        "",
                    ]
                    + offenders
                )
            )

    def test_theme_links_block_does_not_inherit_default_ckan_favicon(self):
        base_template = REPO_ROOT / "ckanext/cwbi_theme/templates/base.html"
        text = base_template.read_text(encoding="utf-8")
        links_block = re.search(
            r"{%\s*block\s+links\s*%}(?P<body>.*?){%\s*endblock\s*%}",
            text,
            re.DOTALL,
        )
        self.assertIsNotNone(links_block, "base.html must define a links block")
        self.assertNotIn(
            "super()",
            links_block.group("body"),
            "The inherited CKAN links block emits /images/favicon.ico, which "
            "escapes non-root deployments such as /catalog.",
        )


if __name__ == "__main__":
    unittest.main()
