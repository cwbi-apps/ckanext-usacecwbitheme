# CWBI CKAN Theme

Installable CKAN extension providing Civil Works Business Intelligence branding,
page-specific artwork, and landing-page routes.
The sibling `ckan-ext` repository provides the local CKAN integration environment.

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
python3 -m venv local
source local/bin/activate
npm ci
npm run build
python -m pip install build
python -m build --wheel
```
 ### Using local env
```bash
python3 -m venv local
    source local/bin/activate
  npm ci
npm run build
python3 -m pip install build
python3 -m build --wheel
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

```bash
cp dist/ckanext_cwbi_theme-0.1.0-py3-none-any.whl ../cwbi-datacatalog-ckan/ckan/local-wheels/
```

## Unit Tests

Run the local unit test suite from this repository:

```bash
python3 -m unittest discover -s tests
```

## Live CKAN Template Tests

These integration tests request rendered pages from a running CKAN instance
with `cwbi_theme` installed and enabled. Set the base URL to include any
deployment path, then run:

```bash
CKAN_LIVE_BASE_URL=http://localhost:5001/ \
  python3 -m unittest discover -s tests/live_ckan -p 'test_*.py'
```

The tests check the rendered `/modules` index and dataset search pages for the
Modules labels, and verify that legacy `/organization` URLs redirect to
`/modules`.

### Start a local CKAN

Docker Compose starts CKAN 2.12 with PostgreSQL, Solr, and Redis. The theme is
installed from this checkout and mounted into the development container.

```bash
docker compose -f docker-compose.live.yml up --build
```

Once CKAN is ready at `http://localhost:5001`, run the live tests in another
terminal using the command above. Stop the environment with:

```bash
docker compose -f docker-compose.live.yml down
```

The local sysadmin login is `ckan_admin` / `test1234`. Override the defaults by
setting `CKAN_SYSADMIN_NAME`, `CKAN_SYSADMIN_PASSWORD`, and
`CKAN_SYSADMIN_EMAIL` before starting Compose. The CKAN port is bound to
localhost, and this setup uses PostgreSQL trust authentication; neither it nor
the default credentials are suitable for deployment.
