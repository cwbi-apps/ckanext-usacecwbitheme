#!/usr/bin/env python3
"""
Verify DCAT import success
"""
import requests

CKAN_URL = 'http://localhost:5000'
JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJPSkhHZHlMZ0NISmYwVmo0TTJ2d0s5Y01jdUt0Mml2MG9TMjhXSGZjaDNJIiwiaWF0IjoxNzcxMDE5MzU5fQ.tUVMNyKxq8zVZe16LCYh9DYMWGQuE1OSw1z5r32dE0o'

def list_packages():
    """List all packages in CKAN"""
    headers = {'Authorization': JWT_TOKEN}

    response = requests.get(
        f'{CKAN_URL}/api/3/action/package_list',
        headers=headers
    )

    result = response.json()
    if result.get('success'):
        packages = result['result']
        print(f"Total packages: {len(packages)}\n")
        for pkg in packages:
            print(f"  - {pkg}")
        return packages
    else:
        print(f"Error: {result}")
        return []

def show_sample_package(package_name):
    """Show details of a sample package"""
    headers = {'Authorization': JWT_TOKEN}

    response = requests.get(
        f'{CKAN_URL}/api/3/action/package_show?id={package_name}',
        headers=headers
    )

    result = response.json()
    if result.get('success'):
        pkg = result['result']
        print(f"\nSample Package: {pkg['title']}")
        print(f"  Name: {pkg['name']}")
        print(f"  URL: {CKAN_URL}/dataset/{pkg['name']}")
        print(f"  Description: {pkg['notes'][:100]}...")
        print(f"  Organization: {pkg.get('organization', {}).get('title', 'N/A')}")
        print(f"  Resources: {len(pkg.get('resources', []))}")
        print(f"  Tags: {[t['name'] for t in pkg.get('tags', [])]}")

        # Show identifier from extras
        for extra in pkg.get('extras', []):
            if extra['key'] == 'identifier':
                print(f"  Identifier: {extra['value']}")
                break
    else:
        print(f"Error: {result}")

if __name__ == '__main__':
    packages = list_packages()
    if packages:
        show_sample_package(packages[0])
