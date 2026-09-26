# HPO (Human Phenotype Ontology)

## Base URL
```
https://ontology.jax.org/api/hp
```

## Auth
No API key required.

## Important: URL-encode colons in HP IDs — `HP:0001250` becomes `HP%3A0001250`

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/search?q={query}&limit={n}&page={p}` | Search HPO terms by name, ID or synonym |
| `/terms/{id}` | Term details |
| `/terms/{id}/children` | Child terms in hierarchy |
| `/terms/{id}/parents` | Parent terms |
| `https://ontology.jax.org/api/network/annotation/{id}` | Annotations (separate `/api/network` base). With an HP ID: associated genes and diseases. With `NCBIGene:{id}` or `OMIM:{id}`/`ORPHA:{id}`: annotated phenotypes |

## Example Calls
```
# Search for "seizure"
https://ontology.jax.org/api/hp/search?q=seizure&limit=5

# Term details for Seizure
https://ontology.jax.org/api/hp/terms/HP%3A0001250

# Genes and diseases associated with Seizure
https://ontology.jax.org/api/network/annotation/HP%3A0001250

# Phenotypes for SCN1A (Entrez 6323)
https://ontology.jax.org/api/network/annotation/NCBIGene%3A6323

# Phenotypes for a disease
https://ontology.jax.org/api/network/annotation/OMIM%3A154700
```

## Response Format
JSON. Search: `terms[]`, `totalCount`. Terms: `id`, `name`, `definition`, `synonyms`. Annotations for an HP term: `genes[]` and `diseases[]`, entries keyed by `id` and `name` (e.g. `NCBIGene:6323` / `SCN1A`). Interactive docs: https://ontology.jax.org/api/hp/docs and https://ontology.jax.org/api/network/docs

## Rate Limits
No published limits. Bulk annotation files at https://hpo.jax.org/data/annotations
