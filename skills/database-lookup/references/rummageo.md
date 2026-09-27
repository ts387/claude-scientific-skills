# RummaGEO (GEO Gene Set Enrichment Search)

## Base URL
```
https://rummageo.com/
```

## Auth
No auth required.

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graphql` | POST | GraphQL API (PostGraphile) for gene set search, metadata filtering and enrichment analysis |

## Example Call
Enrichment is run against a species-specific background. First list the backgrounds (human, mouse), then call `enrich` on the chosen one:
```bash
# 1. Get background ids
curl -X POST "https://rummageo.com/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ backgrounds { nodes { id species } } }"}'

# 2. Enrich a gene list against that background
curl -X POST "https://rummageo.com/graphql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query Enrich($id: UUID!, $genes: [String]!, $first: Int) { background(id: $id) { enrich(genes: $genes, first: $first) { nodes { pvalue adjPvalue oddsRatio nOverlap geneSets { nodes { term } } } } } }",
    "variables": {"id": "<background id>", "genes": ["BRCA1","TP53","EGFR","MYC","PTEN"], "first": 10}
  }'
```

Schema and source: https://github.com/MaayanLab/rummageo

## Response Format
JSON (GraphQL `data` envelope). Ranked list of matching GEO signatures with p-values, adjusted p-values, odds ratios and overlap counts.

## Note
POST endpoint — use `curl` via shell, not WebFetch.

## Rate Limits
No published limits. Designed for interactive/programmatic use.
