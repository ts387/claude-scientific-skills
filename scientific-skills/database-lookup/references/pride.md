# PRIDE Archive REST API Reference

## Overview
PRIDE (PRoteomics IDEntifications Database) at EMBL-EBI provides a full public REST API for querying proteomics datasets, proteins, peptides, and spectra.

## Base URL
```
https://www.ebi.ac.uk/pride/ws/archive/v3
```
v3 is the current API; v2 (`/ws/archive/v2`) was retired in January 2025. The endpoint paths and filter syntax below were written for v2; check each against the official API docs (https://www.ebi.ac.uk/pride/markdownpage/prideapi) before use. Project keyword search in v3 is `GET /search/projects?keyword=...`.

## Authentication
- **No authentication required** for read access
- Open and free to use

## Key Endpoints

| Endpoint | Description |
|---|---|
| `GET /search/projects` | Search proteomics projects by keyword (v3) |
| `GET /projects/{accession}` | Get a specific project by PXD accession |
| `GET /projects/{accession}/files` | List files for a project |
| `GET /spectra` | Search spectra |
| `GET /peptideevidences` | Search peptide evidences |
| `GET /proteinevidences` | Search protein evidences |
| `GET /stats` | Database statistics |

## Query Parameters
- `keyword` — free-text search
- `filter` — field-specific filters (e.g., species, instrument, modification)
- `pageSize` — results per page (default 10, max 100)
- `page` — page number (0-indexed)
- `sortDirection` — ASC or DESC
- `sortFields` — field to sort by

## Example Calls

```bash
# Search projects by keyword
curl "https://www.ebi.ac.uk/pride/ws/archive/v3/search/projects?keyword=alzheimer&pageSize=5"

# Get a specific project
curl "https://www.ebi.ac.uk/pride/ws/archive/v3/projects/PXD010000"

# The remaining examples use v2 paths (v2 is retired); confirm the v3 equivalents in the API docs
# List files for a project
curl "https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD010000/files?pageSize=10"

# Search by species (human = 9606)
curl "https://www.ebi.ac.uk/pride/ws/archive/v2/projects?filter=organisms_facet==9606&pageSize=5"

# Get database statistics
curl "https://www.ebi.ac.uk/pride/ws/archive/v2/stats"
```

## Response Format
JSON. Example (project):
```json
{
  "accession": "PXD010000",
  "title": "Project title here",
  "projectDescription": "...",
  "organisms": [{"accession": "9606", "name": "Homo sapiens"}],
  "instruments": [{"name": "Q Exactive"}],
  "submissionDate": "2018-05-01",
  "publicationDate": "2018-09-01",
  "numAssays": 12,
  "references": [{"pubmedId": 12345678}]
}
```

## Rate Limits
- No strict published rate limits, but standard EBI fair-use policies apply
- Recommended: limit to a few requests per second
- Bulk data available via FTP/Aspera at ftp.pride.ebi.ac.uk
