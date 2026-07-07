# CWBI CKAN Theme

Installable CKAN extension providing Civil Works Business Intelligence branding,
page-specific artwork, and landing-page routes.

## Install

Install the repository or a built distribution into the target CKAN environment:

```bash
pip install .
```

Enable the plugin in CKAN:

```ini
ckan.plugins = ... cwbi_theme
```

## Build

```bash
npm ci
npm run build
python -m pip install build
python -m build --wheel
```

`tailwind.css` is the canonical stylesheet source. The Tailwind build generates
`ckanext/cwbi_theme/assets/cwbi-theme.css`, which CKAN loads at runtime. Do not
edit the generated CSS directly.

CKAN-owned header and footer classes styled by the theme are safelisted in
`tailwind.config.cjs` because those classes do not appear in this extension's
templates. `tailwind.config.cjs` is the only active Tailwind configuration.

The Python distribution includes the generated CSS, templates, and graphical
assets.

After that, stage the wheel into CKAN:

```powershell
Copy-Item dist\ckanext_cwbi_theme-0.1.0-py3-none-any.whl ..\cwbi-datacatalog-ckan\ckan\local-wheels\ -Force
```

## Unit Tests

Run the local unit test suite from this repository:

```bash
python -m unittest discover -s tests
```
