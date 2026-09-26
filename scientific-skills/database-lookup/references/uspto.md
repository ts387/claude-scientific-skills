# USPTO Public APIs

## 1. PatentsView API (Primary Patent Search)

The newer Elasticsearch-based API is the recommended endpoint.

### Base URL

```
https://search.patentsview.org/api/v1/
```

**API key required** — register at `https://patentsview.org/apis/keyrequest`

Pass as query parameter: `?api_key=YOUR_KEY`

### Key Endpoints

#### Search patents
```
GET or POST /patent/
```

Query parameter `q` accepts a JSON query object.

Operators: `_eq`, `_neq`, `_gt`, `_gte`, `_lt`, `_lte`, `_begins`, `_contains`, `_text_any`, `_text_all`, `_text_phrase`, `_and`, `_or`, `_not`

Parameters:
- `q` — JSON query
- `f` — fields to return (JSON array)
- `o` — options: `{"size": 25}` for pagination
- `s` — sort: `[{"patent_date": "desc"}]`

#### Search by keyword
```
GET /patent/?q={"_text_any":{"patent_abstract":"autonomous vehicle"}}&f=["patent_id","patent_title","patent_date"]&o={"size":5}&api_key=KEY
```

#### Search by inventor
```
GET /patent/?q={"inventors.inventor_name_last":"Tesla"}&f=["patent_id","patent_title","patent_date"]&api_key=KEY
```

#### Search by assignee
```
GET /patent/?q={"assignees.assignee_organization":"Google LLC"}&f=["patent_id","patent_title","patent_date","assignees"]&api_key=KEY
```

#### Lookup by patent number
```
GET /patent/{patent_number}/?api_key=KEY
```

#### Other entity endpoints
```
/inventor/
/assignee/
/cpc_group/
```

### Response Structure

```json
{
  "patents": [
    {
      "patent_id": "11234567",
      "patent_title": "...",
      "patent_date": "2022-03-15",
      "patent_abstract": "...",
      "assignees": [{"assignee_organization": "..."}],
      "inventors": [{"inventor_name_first": "...", "inventor_name_last": "..."}]
    }
  ],
  "count": 1,
  "total_hits": 8923
}
```

### Rate Limits

~45 requests per minute per API key.

### Important Note

The user must have a PatentsView API key for this endpoint. If they don't have one, let them know they need to register at `https://patentsview.org/apis/keyrequest`. Load the key from `.env` as `PATENTSVIEW_API_KEY`.

**Note:** The legacy API at `api.patentsview.org` has been decommissioned (returns 410 Gone). Only the new API above works.

## 2. Patent File Wrapper — USPTO Open Data Portal (ODP)

For patent prosecution data (application status, filing dates, examiner info, transactions, documents). This replaced the Patent Examination Data System (PEDS, `ped.uspto.gov`), which was retired on March 14, 2025.

**Base URL**: `https://api.uspto.gov/api/v1/patent/applications/`

**API key required** — sign in at `https://data.uspto.gov/apikey` with a USPTO.gov account (MFA and ID verification required). Send it as the `X-API-KEY` header. Load the key from `.env` as `USPTO_API_KEY`.
Since 18 June 2026 the whole Open Data Portal (including `data.uspto.gov/apikey` and the API docs) requires signing in, so these URLs will not open anonymously in a browser, and every `api.uspto.gov` request without a valid `X-API-KEY` is rejected. If the user has no key, tell them to create one; do not treat a 401/403 as the endpoint being wrong.

```
# One application (bibliographic/application data)
GET https://api.uspto.gov/api/v1/patent/applications/{applicationNumberText}

# Documents in the file wrapper (with download URIs)
GET https://api.uspto.gov/api/v1/patent/applications/{applicationNumberText}/documents

# Search (GET with ?q=..., or POST with a JSON query body; see the ODP Search API docs)
GET https://api.uspto.gov/api/v1/patent/applications/search?q=applicationNumberText:16123456
```

```bash
curl -H "X-API-KEY: $USPTO_API_KEY" \
  "https://api.uspto.gov/api/v1/patent/applications/search?q=applicationNumberText:16123456"
```

Covers applications filed after January 1, 2001; refreshed daily. Full endpoint reference and query syntax: `https://data.uspto.gov/apis/getting-started`.

## 3. TSDR — Trademark Status & Document Retrieval

For trademark lookup by serial or registration number (not full-text search).

```
GET https://tsdrapi.uspto.gov/ts/cd/casestatus/sn{serial_number}/info.xml
GET https://tsdrapi.uspto.gov/ts/cd/casestatus/rn{registration_number}/info.xml
```

Returns XML with mark details, status, owner, goods/services, prosecution history.

**API key required** (since October 2020): request a TSDR key with a USPTO.gov account in the API Key Manager (`https://account.uspto.gov/api-manager/`) and send it in the `USPTO-API-KEY` request header. Load it from `.env` as `USPTO_TSDR_API_KEY`. Rate limited to 60 requests/min per key (4/min for PDF and ZIP downloads).

```bash
curl -H "USPTO-API-KEY: $USPTO_TSDR_API_KEY" \
  "https://tsdrapi.uspto.gov/ts/cd/casestatus/sn78787878/info.xml"
```

## 4. Limitations

- **No public REST API for trademark full-text search** (the USPTO Trademark Search tool at `https://tmsearch.uspto.gov`, which replaced TESS in November 2023, is web-only)
- PatentsView new API requires registration for an API key
- The ODP Patent File Wrapper API requires an API key (USPTO.gov account at `https://data.uspto.gov/apikey`)
- TSDR requires an API key and knowing the serial/registration number already
