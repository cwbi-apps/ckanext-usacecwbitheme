from setuptools import setup, find_namespace_packages

setup(
    name="ckanext-usace-theme",
    version="0.1.0",
    packages=find_namespace_packages(include=["ckanext.*"]),
    include_package_data=True,
    entry_points={
        "ckan.plugins": [
            "usace_theme = ckanext.usace_theme.plugin:UsaceThemePlugin",
        ],
    },
)
