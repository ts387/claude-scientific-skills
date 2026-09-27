# medRxiv API

medRxiv is a preprint server for health sciences. The API is identical to bioRxiv's API -- same endpoints, same response format -- just use `medrxiv` as the server parameter.

**Important:** Like bioRxiv, there is **no keyword search**. Use Semantic Scholar, OpenAlex, or PubMed for keyword searches of medRxiv content.

## Base URL

```
https://api.biorxiv.org
```

(Same base URL as bioRxiv -- the server is specified in the path.)

**Use `api.biorxiv.org`, not `api.medrxiv.org`.** The `api.medrxiv.org` host answers some paths but
is not equivalent, and its failures are not graceful (verified 2026-07-27):

| Request | Result |
|---|---|
| `api.medrxiv.org/details/medrxiv/10d` | **HTTP 500**, empty body |
| `api.medrxiv.org/details/medrxiv/2024-01-01/2024-01-03/0` | 200, but `count: 60` -- returns the whole interval, ignoring the documented page size, and omits `category` from `messages` |
| `api.biorxiv.org/details/medrxiv/2024-01-01/2024-01-03/0` | 200, `count: 30`, full `messages` block |

Every example below uses `api.biorxiv.org`.

## Authentication

None required. Fully public API.

## Key Endpoints

### 1. Content Detail -- Browse by date range

```
GET /details/medrxiv/{interval}/{cursor}/{format}
```

| Parameter | Values | Description |
|-----------|--------|-------------|
| `interval` | `YYYY-MM-DD/YYYY-MM-DD` | Date range (inclusive) |
| | `N` (integer) | N most recent preprints |
| | `Nd` (integer + "d") | Last N days |
| `cursor` | Integer (default `0`) | Absolute record offset. **`/details/` returns 30 per page, so step by 30** -- see Pagination. |
| `format` | `json` (default), `xml` | Response format |

Optional: `?category=cardiovascular_medicine` (use underscores for spaces; the API returns the name with spaces, e.g. "cardiovascular medicine")

**Examples:**
```
https://api.biorxiv.org/details/medrxiv/2024-01-01/2024-01-31/0
https://api.biorxiv.org/details/medrxiv/5
https://api.biorxiv.org/details/medrxiv/10d
```

### 2. Content Detail -- DOI lookup

```
GET /details/medrxiv/{doi}/na/{format}
```

**Example:**
```
https://api.biorxiv.org/details/medrxiv/10.1101/2021.04.29.21256344/na/json
```

### 3. Published Article Links

```
GET /pubs/medrxiv/{interval}/{cursor}
GET /pubs/medrxiv/{doi}/na
```

Links preprints to their published journal versions. Accepts both preprint DOI and published DOI.

## Response Format

Same as bioRxiv:

```json
{
  "messages": [{
    "status": "ok",
    "category": "all",
    "interval": "2024-01-01:2024-01-03",
    "funder": "all",
    "cursor": 0,
    "count": 30,
    "count_new_papers": "46",
    "total": "60"
  }],
  "collection": [{
    "title": "Paper title...",
    "authors": "Surname, A.; Surname, B.",
    "author_corresponding": "Full Name",
    "author_corresponding_institution": "Institution",
    "doi": "10.1101/2021.04.29.21256344",
    "date": "2021-05-03",
    "version": "1",
    "type": "PUBLISHAHEADOFPRINT",
    "license": "cc_by_nc_nd",
    "category": "cardiovascular medicine",
    "abstract": "Full abstract text...",
    "published": "10.1371/journal.pone.0256482",
    "server": "medRxiv"
  }]
}
```

## Pagination

**30 results per page on `/details/`, 100 on `/pubs/`** -- same as bioRxiv, and the same silent
hazard: `cursor` is an absolute record offset, out-of-step values return HTTP 200, and stepping a
`/details/` walk by 100 skips records 30-99 of every hundred while looking successful. Step by the
`count` the response reported. See the Pagination and `messages` sections of
`references/biorxiv.md` for the full behavior, including why `total` and `count_new_papers` differ
and which endpoints expose no counts at all.

`scripts/paginate.py --api medrxiv` implements the walk with the correct step.

## Rate Limits

No documented rate limits. No authentication required.

## Categories

`addiction_medicine`, `allergy_and_immunology`, `anesthesia`, `cardiovascular_medicine`, `dentistry_and_oral_medicine`, `dermatology`, `emergency_medicine`, `endocrinology`, `epidemiology`, `forensic_medicine`, `gastroenterology`, `genetic_and_genomic_medicine`, `geriatric_medicine`, `health_economics`, `health_informatics`, `health_policy`, `health_systems_and_quality_improvement`, `hematology`, `hiv_aids`, `infectious_diseases`, `intensive_care_and_critical_care_medicine`, `medical_education`, `medical_ethics`, `nephrology`, `neurology`, `nursing`, `nutrition`, `obstetrics_and_gynecology`, `occupational_and_environmental_health`, `oncology`, `ophthalmology`, `orthopedics`, `otolaryngology`, `pain_medicine`, `palliative_medicine`, `pathology`, `pediatrics`, `pharmacology_and_therapeutics`, `primary_care_research`, `psychiatry_and_clinical_psychology`, `public_and_global_health`, `radiology_and_imaging`, `rehabilitation_medicine_and_physical_therapy`, `respiratory_medicine`, `rheumatology`, `sexual_and_reproductive_health`, `sports_medicine`, `surgery`, `toxicology`, `transplantation`, `urology`
