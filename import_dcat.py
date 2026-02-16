#!/usr/bin/env python3
"""
Import DCAT-US catalog into CKAN
"""
import json
import requests
import sys
from urllib.parse import quote

CKAN_URL = 'http://localhost:5000'
# JWT API token for default user (sysadmin)
API_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJPSkhHZHlMZ0NISmYwVmo0TTJ2d0s5Y01jdUt0Mml2MG9TMjhXSGZjaDNJIiwiaWF0IjoxNzcxMDE5MzU5fQ.tUVMNyKxq8zVZe16LCYh9DYMWGQuE1OSw1z5r32dE0o'
ORG_NAME = 'test-org'

def create_package_from_dcat(dataset, org_name, attempt=0):
    """Convert DCAT dataset to CKAN package format and create it"""
    import re

    # Basic package metadata
    # Generate a valid CKAN package name from the identifier
    identifier = dataset.get('identifier', 'dataset')
    parts = identifier.split('/')

    # Try to get a meaningful name from the identifier
    # For URLs like /services/LayerName/MapServer/0, take LayerName-0
    if len(parts) >= 2:
        # Get last 2-3 parts depending on what makes sense
        if len(parts[-1]) < 2 or parts[-1].isdigit():
            # Last part is just a number, include the one before it
            name_base = '-'.join(parts[-3:]) if len(parts) >= 3 else '-'.join(parts[-2:])
        else:
            name_base = parts[-1]
    else:
        name_base = identifier

    # Clean up the name
    name_base = name_base.lower().replace(':', '-').replace('/', '-').replace(' ', '-').replace('_', '-')

    # Remove repeated dashes
    name_base = re.sub(r'-+', '-', name_base).strip('-')

    # If name is still too short, prepend 'dataset-'
    if len(name_base) < 2:
        name_base = f"dataset-{name_base}"

    # Add suffix for duplicate attempts
    if attempt > 0:
        suffix = f"-{attempt}"
        max_base_len = 100 - len(suffix)
        package_name = name_base[:max_base_len] + suffix
    else:
        package_name = name_base[:100]

    package = {
        'name': package_name,
        'title': dataset.get('title', 'Untitled'),
        'notes': dataset.get('description', ''),
        'owner_org': org_name,
        'tags': [{'name': kw.lower()[:100]} for kw in dataset.get('keyword', [])[:10]],
        'extras': []
    }

    # Add identifier as extra
    package['extras'].append({
        'key': 'identifier',
        'value': dataset.get('identifier', '')
    })

    # Add spatial extent if available
    if 'spatial' in dataset:
        package['extras'].append({
            'key': 'spatial',
            'value': dataset['spatial']
        })

    # Add publisher
    if 'publisher' in dataset:
        publisher_name = dataset['publisher'].get('name', '')
        package['extras'].append({
            'key': 'publisher',
            'value': publisher_name
        })

    # Add contact point
    if 'contactPoint' in dataset:
        contact_name = dataset['contactPoint'].get('fn', '')
        contact_email = dataset['contactPoint'].get('hasEmail', '').replace('mailto:', '')
        if contact_name:
            package['maintainer'] = contact_name
        if contact_email:
            package['maintainer_email'] = contact_email

    # Add license
    if 'license' in dataset:
        package['license_url'] = dataset['license']

    # Create resources from distributions
    package['resources'] = []
    for dist in dataset.get('distribution', []):
        resource = {
            'name': dist.get('title', 'Resource'),
            'description': dist.get('description', ''),
            'url': dist.get('accessURL', ''),
            'format': dist.get('format', 'API')
        }
        if 'mediaType' in dist:
            resource['mimetype'] = dist['mediaType']
        package['resources'].append(resource)

    # Create package via API
    headers = {
        'Authorization': API_TOKEN,
        'Content-Type': 'application/json'
    }
    response = requests.post(
        f'{CKAN_URL}/api/3/action/package_create',
        headers=headers,
        json=package
    )

    return response

def main():
    # Load DCAT catalog
    with open('dcat_catalog.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    datasets = catalog.get('dataset', [])
    print(f"Found {len(datasets)} datasets to import")

    success_count = 0
    error_count = 0

    for i, dataset in enumerate(datasets):  # Import all datasets
        try:
            # Try to create package, retry with suffix if name already exists
            max_attempts = 5
            response = None

            for attempt in range(max_attempts):
                response = create_package_from_dcat(dataset, ORG_NAME, attempt)

                if response.status_code == 200:
                    result = response.json()
                    if result['success']:
                        success_count += 1
                        print(f"[OK] [{i+1}/{len(datasets)}] {dataset.get('title', 'Untitled')}")
                        break
                    else:
                        error = result.get('error', {})
                        # Check if it's a duplicate name error
                        if isinstance(error, dict) and 'name' in error:
                            error_msgs = error['name']
                            if any('already in use' in str(msg).lower() for msg in error_msgs):
                                # Try again with next attempt number
                                continue
                        # Other validation error, don't retry
                        error_count += 1
                        print(f"[FAIL] [{i+1}] {dataset.get('title')}: {error}")
                        break
                else:
                    error_count += 1
                    print(f"[FAIL] [{i+1}] HTTP {response.status_code}: {response.text[:200]}")
                    break
            else:
                # All attempts failed
                error_count += 1
                print(f"[FAIL] [{i+1}] {dataset.get('title', 'Untitled')}: Could not find unique name after {max_attempts} attempts")

        except Exception as e:
            error_count += 1
            print(f"[FAIL] [{i+1}] Error: {e}")

    print(f"\nImport complete: {success_count} successful, {error_count} errors")

if __name__ == '__main__':
    main()
