# CKAN and Esri REST Services: Technical Findings

**Date**: February 13, 2026
**Context**: Proof of concept for DoD data catalog requirement using CKAN

## Executive Summary

CKAN's built-in ArcGIS harvesting extensions **only support ArcGIS Portal APIs, not ArcGIS REST Services directories**. This is a critical limitation for DoD/government geospatial environments where data is primarily exposed through REST Services endpoints rather than Portal.

**Recommended Architecture**: Custom harvester → DCAT-US 3.0 export → CKAN import via API

## Key Findings

### 1. CKAN ArcGIS Harvesting is Portal-Only

#### Extensions Evaluated

| Extension | Source | Conclusion |
|-----------|--------|------------|
| `ckanext-harvest-basket` | Third-party collection | Portal API only |
| `ckanext-geodatagov` | Official data.gov extension | Portal API only |

#### Evidence

Both harvesters use the ArcGIS Portal API endpoint `/sharing/search`:

```python
# From ckanext-geodatagov/harvesters/arcgis.py:150
search_path = 'sharing/search?f=pjson&q={query}&num={num}&start={start}'.format(
    query=query,
    num=num,
    start=start,
)
```

This endpoint **does not exist** on standard ArcGIS REST Services directories.

#### What This Means

- **Cannot harvest**: `https://example.com/arcgis/rest/services`
- **Can only harvest**: `https://portal.example.com/sharing/search`

For organizations serving geospatial data via ArcGIS Server (not Portal), CKAN's built-in harvesters are non-functional.

### 2. REST Services vs Portal API: Critical Differences

| Aspect | ArcGIS REST Services | ArcGIS Portal |
|--------|---------------------|---------------|
| **Endpoint** | `/arcgis/rest/services` | `/sharing/search` |
| **Purpose** | Direct service access | Catalog/metadata search |
| **Metadata** | Service-level JSON | Portal item metadata |
| **Common in** | Government GIS infrastructure | ArcGIS Online / Enterprise Portal |
| **CKAN Support** | ❌ None | ✅ Via geodatagov |

**DoD/Government Context**: Most military and government installations expose geospatial data through ArcGIS Server REST Services, not Portal, due to:
- Security requirements
- Existing infrastructure
- Simpler deployment model
- Direct service access needs

### 3. DCAT Import: Validated Solution

#### Proof of Concept Results

- **Input**: 379 datasets from custom metadata catalog
- **Format**: DCAT-US 3.0 JSON-LD
- **Success Rate**: 90% (341/379 datasets imported)
- **Failures**: Tag validation (special characters), duplicate names

#### Import Performance

```
Total datasets: 379
Successful: 341 (90%)
Failed: 38 (10%)
  - Invalid tags: ~28 (tags with parentheses, brackets)
  - Duplicate names: ~10 (identical service layer names)
```

#### Metadata Preservation

✅ **Successfully preserved**:
- Original REST Services URL (as identifier in extras)
- Title and description
- Keywords/tags (when valid)
- Resources (service endpoints)
- Organization membership

### 4. CKAN API Authentication (2.11+)

#### Critical Discovery

CKAN 2.9+ moved from simple API keys to **JWT-based tokens**.

**Old approach (pre-2.9)** - ❌ Does not work:
```python
headers = {'X-CKAN-API-Key': '4b593a75-514e-4163-a06e-8ef31ff7174b'}
```

**New approach (2.9+)** - ✅ Required:
```python
# Create token via CLI
ckan user token add <username> <token-name>

# Use in API calls
headers = {'Authorization': 'eyJhbGci...'}  # JWT token
```

**Configuration**:
```ini
# From ckan.ini
apitoken_header_name = Authorization
```

See [API_AUTH_SOLUTION.md](API_AUTH_SOLUTION.md) for complete details.

### 5. CKAN Validation Rules

#### Tag Constraints

Tags must contain **only**:
- Alphanumeric characters
- Spaces
- Hyphens (`-`)
- Underscores (`_`)
- Periods (`.`)

❌ **Rejected**: `(point)`, `[place]`, `(polygon)`, etc.

**Impact**: Keywords from GIS metadata often contain geometry types in parentheses, which CKAN rejects.

**Mitigation**: Sanitize tags during DCAT export or import process.

#### Name Constraints

- Minimum 2 characters
- Maximum 100 characters
- Must be unique across the CKAN instance
- URL-safe characters only

**Impact**: Service layer identifiers like `MapServer/0` require transformation to valid CKAN names.

## Architectural Implications

### What CKAN Provides

✅ **Strengths**:
- Robust data catalog UI
- RESTful API
- Organization/permission management
- Resource management
- DCAT-US 3.0 compatibility (via ckanext-dcat)
- Search/discovery capabilities
- Spatial metadata support (via ckanext-spatial)

❌ **Limitations**:
- No REST Services directory harvesting
- Strict validation rules (tags, names)
- Requires external harvesting solution

### Recommended Integration Architecture

```
┌─────────────────────────────┐
│  ArcGIS REST Services       │
│  /arcgis/rest/services      │
└──────────┬──────────────────┘
           │
           │ HTTP/JSON
           ▼
┌─────────────────────────────┐
│  Custom Metadata Catalog    │
│  - Harvests Service JSON    │
│  - Harvests Layer metadata  │
│  - Semantic alignment       │
│  - Exports DCAT-US 3.0      │
└──────────┬──────────────────┘
           │
           │ dcat_catalog.json
           ▼
┌─────────────────────────────┐
│  import_dcat.py             │
│  - JWT authentication       │
│  - Tag sanitization         │
│  - Name uniqueness          │
│  - Error handling           │
└──────────┬──────────────────┘
           │
           │ CKAN API
           ▼
┌─────────────────────────────┐
│  CKAN Instance              │
│  - Catalog UI               │
│  - Search/discovery         │
│  - API access               │
│  - User management          │
└─────────────────────────────┘
```

### Why This Architecture Works

1. **Separation of Concerns**
   - Custom catalog: REST Services harvesting expertise
   - CKAN: Catalog management and user interface

2. **Standards-Based Integration**
   - DCAT-US 3.0 is the official federal metadata standard
   - Loose coupling via standard format
   - Each component can be upgraded independently

3. **Metadata Enrichment**
   - Custom catalog can extract detailed GIS metadata
   - DCAT provides semantic mapping
   - CKAN receives clean, validated metadata

4. **Scalability**
   - Custom catalog handles heavy lifting (REST API calls)
   - CKAN receives processed metadata in bulk
   - Proven to handle 300+ datasets efficiently

## Comparison: CKAN vs GeoPortal Server

| Aspect | CKAN | GeoPortal Server |
|--------|------|------------------|
| **REST Services Harvesting** | ❌ Not built-in | ✅ Native support |
| **Maintenance** | ✅ Active (2.11.4) | ⚠️ Limited updates |
| **Docker Support** | ✅ Official images | ⚠️ Community only |
| **API** | ✅ Modern REST | ⚠️ CSW-based |
| **UI Customization** | ✅ Extensions/themes | ⚠️ JSP modifications |
| **Security Review** | ✅ Passed | ❌ Rejected by security |
| **DCAT Support** | ✅ Native (ckanext-dcat) | ⚠️ Via CSW mapping |

## Recommendations

### For This Project

1. **Keep CKAN** - It satisfies the DoD directive for a data catalog
2. **Use Custom Harvester** - Leverage existing metadata catalog's REST Services harvesting
3. **DCAT Pipeline** - Proven integration path (90% success rate)
4. **Tag Sanitization** - Add to DCAT export to remove special characters

### For Production Deployment

#### Required Components

1. **Custom Metadata Catalog** (already exists)
   - Harvests ArcGIS REST Services
   - Exports DCAT-US 3.0

2. **CKAN Instance** (proven in PoC)
   - Version 2.11.4 or later
   - Extensions: spatial, dcat, harvest (for other sources)

3. **Integration Script** ([import_dcat.py](import_dcat.py))
   - JWT authentication
   - Tag sanitization
   - Duplicate handling
   - Error logging

4. **Automation** (future)
   - Scheduled DCAT export from catalog
   - Automated import to CKAN
   - Differential updates (only changed datasets)

#### Deployment Considerations

**Security**:
- JWT tokens should be rotated regularly
- Use environment variables for tokens (not hardcoded)
- HTTPS required for production
- Consider CKAN's built-in authentication integration (LDAP/SAML)

**Performance**:
- Batch imports (tested: 379 datasets in ~8 minutes)
- Consider incremental updates vs full refresh
- Monitor CKAN database size

**Maintenance**:
- Custom catalog handles REST Services changes
- CKAN updates are independent
- DCAT format is stable (federal standard)

## Open Questions

1. **Tag Sanitization**: Where to implement?
   - Option A: In custom catalog's DCAT export
   - Option B: In import_dcat.py script
   - **Recommendation**: Custom catalog (cleaner separation)

2. **Update Strategy**: Full refresh or differential?
   - Full refresh: Simple, tested, works for ~400 datasets
   - Differential: More complex, better for 1000+ datasets
   - **Recommendation**: Start with full refresh, add differential if needed

3. **Error Handling**: How to handle the 10% failures?
   - Manual review and fix?
   - Automated retries with modified metadata?
   - Accept 90% as sufficient?
   - **Recommendation**: Log failures, review quarterly, fix if critical

4. **Multi-Instance**: Can custom catalog feed multiple CKAN instances?
   - Answer: Yes, DCAT export is instance-independent
   - Benefit: Dev/test/prod environments

## Conclusion

**CKAN cannot directly harvest ArcGIS REST Services directories**, but it can successfully serve as a data catalog when paired with a custom harvesting solution.

The **custom catalog → DCAT-US 3.0 → CKAN** architecture is:
- ✅ Standards-based (DCAT-US 3.0)
- ✅ Proven (90% success rate in PoC)
- ✅ Scalable (handles 300+ datasets efficiently)
- ✅ Maintainable (loose coupling, clear separation of concerns)
- ✅ DoD-compliant (satisfies directive for data catalog)

This approach leverages the strengths of both systems:
- Custom catalog: Geospatial harvesting expertise
- CKAN: Catalog management and user experience

## References

- [import_dcat.py](import_dcat.py) - Working import script
- [API_AUTH_SOLUTION.md](API_AUTH_SOLUTION.md) - JWT authentication details
- [ckanext-geodatagov source](https://github.com/GSA/ckanext-geodatagov) - Confirms Portal-only harvesting
- [DCAT-US 3.0 Specification](https://resources.data.gov/resources/dcat-us/) - Federal metadata standard

---

**Status**: Proof of concept complete
**Next Steps**: Production deployment planning, tag sanitization implementation
