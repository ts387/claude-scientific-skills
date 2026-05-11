# OpenAlex (Scholarly Works, Authors, Institutions)

## Base URL
```
https://api.openalex.org
```

OpenAlex is a free, open catalog of 240M+ scholarly works, plus authors, sources (journals), institutions, topics, publishers, and funders.

## Auth
No API key. Append `?mailto=you@example.edu` (or `&mailto=`) to enter the "polite pool" — 10 req/s instead of 1 req/s, same 100k/day cap.

## Entity Endpoints

| Endpoint | Contents |
|----------|----------|
| `/works` | Scholarly documents (papers, books, datasets) |
| `/authors` | Researcher profiles |
| `/sources` | Journals, repositories, conferences |
| `/institutions` | Universities, research orgs |
| `/topics` | 3-level subject hierarchy |
| `/publishers` | Publishing organizations |
| `/funders` | Funding agencies |
| `/text` | POST plain text to be auto-tagged with topics/keywords |

Get a specific entity by ID: `/works/W2741809807`, `/authors/A5023888391`, etc.

## Essential Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `filter=` | Apply filters (comma = AND) | `filter=publication_year:2023,is_oa:true` |
| `search=` | Full-text search | `search=machine+learning` |
| `sort=` | Sort | `sort=cited_by_count:desc` |
| `per-page=` | Page size (max 200) | `per-page=200` |
| `page=` | Page number | `page=2` |
| `sample=` | Random sample (use `seed=`) | `sample=50&seed=42` |
| `select=` | Limit returned fields | `select=id,title,doi` |
| `group_by=` | Aggregate by field | `group_by=publication_year` |
| `mailto=` | Polite pool email | `mailto=you@example.edu` |

## Filter Syntax

```
Single:        filter=publication_year:2020
AND:           filter=publication_year:2020,is_oa:true
OR (pipe):     filter=type:journal-article|book
Negation:      filter=type:!journal-article
Comparison:    filter=cited_by_count:>100
Range:         filter=publication_year:2020-2023
```

Up to 50 values per pipe-OR — useful for batch ID/DOI lookup.

## Critical Best Practices

- **Always use `sample=` for random sampling**; never random `page=N` — that biases by sort order.
- **Two-step lookup for entity filtering**: search `/authors?search=NAME` → grab ID → `/works?filter=authorships.author.id:ID`. Don't filter by free-text names.
- **Use `per-page=200`** — 8× faster than the default 25.
- **Batch with pipe OR** (`filter=doi:X|Y|Z`) instead of N sequential requests.
- **Add `mailto=`** for the 10× rate-limit boost.

## Example Calls

```
# Search
https://api.openalex.org/works?search=CRISPR+gene+editing&per-page=10&mailto=you@example.edu

# Recent open-access works on a topic, most-cited first
https://api.openalex.org/works?search=climate&filter=publication_year:>2020,is_oa:true&sort=cited_by_count:desc&per-page=200

# Works by an author (two-step)
https://api.openalex.org/authors?search=Jennifer+Doudna&per-page=1
https://api.openalex.org/works?filter=authorships.author.id:A5023888391

# Works by an institution (two-step)
https://api.openalex.org/institutions?search=MIT
https://api.openalex.org/works?filter=authorships.institutions.id:I136199984

# Bulk DOI lookup (up to 50 values per filter)
https://api.openalex.org/works?filter=doi:10.1371/journal.pone.0266781|10.1371/journal.pone.0267149

# Random sample
https://api.openalex.org/works?sample=50&seed=42

# Aggregate: papers per year for a topic
https://api.openalex.org/works?search=quantum+computing&group_by=publication_year

# Auto-tag arbitrary text with topics/keywords
POST https://api.openalex.org/text  body: {"title":"...", "abstract":"..."}
```

## Response Shape

```json
{
  "meta": {
    "count": 12345,
    "page": 1,
    "per_page": 25
  },
  "results": [ { "id": "...", "title": "...", ... } ],
  "group_by": []
}
```

Single-entity responses return the entity object directly (no `results` wrapper).

## ID Prefixes
- `W` works, `A` authors, `S` sources, `I` institutions, `T` topics, `P` publishers, `F` funders
- Full IDs are URLs (`https://openalex.org/W2741809807`); the last segment works in filters.

## Pagination Beyond Page 10,000

Standard `page=` works up to 10k results. For larger result sets use cursor pagination:
```
?per-page=200&cursor=*           # first page
?per-page=200&cursor=<next>      # use meta.next_cursor from prior response
```

## Bulk Data Snapshot
Full database snapshot is available for download (~hundreds of GB) via the OpenAlex snapshot at `https://docs.openalex.org/download-all-data/openalex-snapshot`. Use for very-large-scale analysis instead of hammering the API.

## Rate Limits
- Default: 1 req/s, 100k req/day
- Polite pool (`mailto=`): 10 req/s, 100k req/day
