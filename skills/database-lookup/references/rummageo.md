# RummaGEO — GEO signature search and enrichment

Public GraphQL endpoint: `https://rummageo.com/graphql`.
The official [application queries](https://github.com/MaayanLab/rummageo/blob/rummageo/src/graphql/core.graphql)
and [server](https://github.com/MaayanLab/rummageo/blob/rummageo/src/lib/postgraphile.ts)
define its query surface. The formerly suggested `/api/enrich` and `/api/table`
REST recipes are not supported by that source.

A small read-only term search (live-tested):
```bash
curl --fail-with-body 'https://rummageo.com/graphql' \
  -H 'Content-Type: application/json' \
  --data '{"query":"{ geneSetTermSearch(terms:[\"neuron\"],first:1,offset:0){ totalCount nodes{term} } }"}'
```

Gene-set enrichment uses `background(id: $id) { enrich(genes: $genes, first: $n,
offset: $offset) { nodes { pvalue adjPvalue oddsRatio nOverlap } totalCount } }`.
Select the appropriate species/background UUID from the service's current
background catalogue before querying. Consult the source for supported filters;
the gene list alone is insufficient to specify the analysis.

Enrichment example — first list the backgrounds (human, mouse), then call `enrich` on the chosen one:
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

Inspect GraphQL `errors` even with HTTP 200. Paginate with `first` and `offset`.
Preserve background, species, signature direction, sample-group contrast and GEO
accession. An enriched signature is an association with a study contrast, not
proof of a causal drug or disease mechanism.
