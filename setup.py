from setuptools import setup, find_namespace_packages

setup(
    name="ckanext-cwbi-theme",
    version="0.1.0",
    packages=find_namespace_packages(include=["ckanext.*"]),
    include_package_data=True,
    package_data={
        "ckanext.cwbi_theme": [
            "assets/*",
            "public/*",
            "templates/*",
            "templates/*/*",
        ],
    },
    entry_points={
        "ckan.plugins": [
            "cwbi_theme = ckanext.cwbi_theme.plugin:CwbiThemePlugin",
        ],
    },
)
