# USPTO Public APIs

## 1. PatentsView → Open Data Portal (ODP)

**Status (checked 2026-08-30):** The PatentsView PatentSearch API that lived at
`https://search.patentsview.org/api/v1/` is **unavailable**. The host no longer
resolves (NXDOMAIN). USPTO migrated PatentsView onto the Open Data Portal on
2026-03-20; PatentSearch and related interactive features are paused with no
published relaunch date. Do **not** call `search.patentsview.org`, do **not**
register at the old `patentsview.org/apis/keyrequest` flow, and do **not** treat
legacy `api.patentsview.org` query URLs as live search endpoints (they redirect
to the transition guide).

### Current access path

Use ODP for PatentsView **bulk datasets** and data dictionaries:

- Transition guide: https://data.uspto.gov/support/transition-guide/patentsview
- PatentsView program page: https://www.uspto.gov/ip-policy/economic-research/patentsview
- ODP home / bulk directory: https://data.uspto.gov/

| Category | Example tables | ODP bulk dataset page |
|---|---|---|
| Granted patents — baseline / disambiguated | `g_patent`, `g_cpc_current`, `g_assignee_disambiguated` | https://data.uspto.gov/bulkdata/datasets/pvgpatdis |
| Granted patents — long text | `g_brf_sum_text_*`, `g_claims_*`, `g_detail_desc_text_*` | https://data.uspto.gov/bulkdata/datasets/pvgpattxt |
| Pre-grant publications — baseline / disambiguated | `pg_published_application`, `pg_cpc_current` | https://data.uspto.gov/bulkdata/datasets/pvpgpubdis |
| Pre-grant publications — long text | `pg_brf_sum_text_*`, `pg_claims_*` | https://data.uspto.gov/bulkdata/datasets/pvpgpubtxt |
| Sorted (beta) | `g_sorted_applicant`, `pg_sorted_individual` | https://data.uspto.gov/bulkdata/datasets/pvsorted |
| Annualized | yearly CSV tables | https://data.uspto.gov/bulkdata/datasets/pvannual |

Data dictionaries (when published) are linked from the “Documents and Resources”
sidebar on each ODP dataset page above.

### Auth for ODP bulk / API access

ODP access requires a USPTO.gov account (MFA). Obtain an **ODP** API key from
https://data.uspto.gov/apikey — previously issued PatentsView PatentSearch keys
are **not** compatible. Prefer loading the key from `.env` as `USPTO_ODP_API_KEY`
and sending it with the header ODP documents for its Bulk Datasets API
(commonly `X-API-KEY`). Never print the key in provenance.

If the user needs interactive keyword / inventor / assignee **search** rather
than bulk tables, say clearly that PatentSearch is paused during the ODP
transition and point them at the transition guide — do not invent a replacement
search URL.

### Historical note

- Legacy PatentsView REST host `api.patentsview.org` is decommissioned for search;
  requests redirect to the ODP transition guide.
- The Elasticsearch PatentSearch base URL `https://search.patentsview.org/api/v1/`
  must not be used until USPTO republishes an ODP-hosted replacement.

## 2. Patent File Wrapper — USPTO Open Data Portal (ODP)

For patent prosecution data (application status, filing dates, examiner info, transactions, documents). This replaced the Patent Examination Data System (PEDS, `ped.uspto.gov`), which was retired on March 14, 2025.

**Base URL**: `https://api.uspto.gov/api/v1/patent/applications/`

**API key required** — the same ODP key described above (USPTO.gov account with MFA and ID verification at `https://data.uspto.gov/apikey`). Send it as the `X-API-KEY` header; load it from `.env` as `USPTO_ODP_API_KEY`.
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
curl -H "X-API-KEY: $USPTO_ODP_API_KEY" \
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

**API key required** (since October 2020): request a TSDR key with a USPTO.gov account in the API Key Manager (`https://account.uspto.gov/api-manager/`) and send it in the `USPTO-API-KEY` request header. This is a separate key from the ODP key. Load it from `.env` as `USPTO_TSDR_API_KEY`. Rate limited to 60 requests/min per key (4/min for PDF and ZIP downloads).

```bash
curl -H "USPTO-API-KEY: $USPTO_TSDR_API_KEY" \
  "https://tsdrapi.uspto.gov/ts/cd/casestatus/sn78787878/info.xml"
```

## 4. Limitations

- **No public REST API for trademark full-text search** (the USPTO Trademark Search tool at `https://tmsearch.uspto.gov`, which replaced TESS in November 2023, is web-only)
- **PatentsView PatentSearch API is paused** during the ODP migration; use ODP
  bulk datasets for PatentsView tables until USPTO republishes search APIs
- The ODP Patent File Wrapper API requires an ODP API key (USPTO.gov account at `https://data.uspto.gov/apikey`)
- TSDR requires its own API key and knowing the serial/registration number already
