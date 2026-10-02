# Monarch Initiative API

## Base URL
```
https://api-v3.monarchinitiative.org/v3/api
```

## Auth
No API key required.

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/search?q={query}` | Text search across all entities |
| `/autocomplete?q={prefix}` | Autocomplete entity names |
| `/entity/{id}` | Entity details (gene, disease, phenotype) |
| `/association?entity={id}` | Associations for an entity (matches subject or object; use `subject={id}` to match subject only) |
| `/association?entity={id}&category={cat}` | Filtered associations (also accepts `predicate`) |
| `/entity/{id}/{category}` | Association table for an entity and one association category (e.g. `/entity/HGNC:3603/biolink:GeneToPhenotypicFeatureAssociation`) |

## Entity ID Prefixes
- `MONDO:` — diseases (e.g. `MONDO:0007947`)
- `HP:` — phenotypes (e.g. `HP:0001250`)
- `HGNC:` — genes (e.g. `HGNC:3603`)
- `NCBIGene:` — genes (e.g. `NCBIGene:7157`)

## Association Categories
`biolink:GeneToPhenotypicFeatureAssociation`, `biolink:DiseaseToPhenotypicFeatureAssociation`, `biolink:GeneToDiseaseAssociation`

## Example Calls
```
# Search for Marfan syndrome
https://api-v3.monarchinitiative.org/v3/api/search?q=Marfan+syndrome&limit=5

# Entity details for a disease
https://api-v3.monarchinitiative.org/v3/api/entity/MONDO:0007947

# Gene-to-phenotype for FBN1
https://api-v3.monarchinitiative.org/v3/api/association?entity=HGNC%3A3603&category=biolink:GeneToPhenotypicFeatureAssociation&limit=10

# Same data via the association-table route
https://api-v3.monarchinitiative.org/v3/api/entity/HGNC:3603/biolink:GeneToPhenotypicFeatureAssociation?limit=10
```

## Response Format
Paginate search/associations with `limit` and zero-based `offset`. JSON. Search: `items[]` with `id`, `name`, `category`. Associations: `items[]` with `subject`, `predicate`, `object`, `publications`.

## Rate Limits
No published limits. Be reasonable.
