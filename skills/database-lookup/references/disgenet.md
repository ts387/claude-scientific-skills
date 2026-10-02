# DISGENET — Gene/variant–disease associations

Use the current [DISGENET documentation](https://www.disgenet.com/docs) and
[API/tools page](https://www.disgenet.com/Tools). The old disgenet.org API and
email/password login recipes are not the current integration contract.

## Base URL
```
https://api.disgenet.com/api/v1
```

## Auth
**API key required.** Access is plan-dependent: the [Academic plan](https://www.disgenet.com/Plans)
exposes the curated subset; full-dataset API access requires an appropriate
subscription. Register at https://www.disgenet.com, then copy the API key from
your profile page. Send the key itself (no `Bearer` prefix) as the `Authorization` header:
```bash
curl -H "Authorization: $DISGENET_API_KEY" -H "accept: application/json" \
  "https://api.disgenet.com/api/v1/gda/summary?gene_ncbi_id=7157&page_number=0"
```

Load the key from `.env` as `DISGENET_API_KEY`.

The base URL is not a browsable page: only the endpoints below respond, and only with a valid key (unauthenticated requests are rejected). The API reference at https://api.disgenet.com is also behind the disgenet.com login. If the user has no key, tell them to register rather than treating the error as a broken endpoint.

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/gda/summary?gene_ncbi_id={id}` (or `gene_symbol=`) | Gene-disease associations for a gene |
| `/gda/summary?disease=UMLS_{cui}` | Gene-disease associations for a disease |
| `/vda/summary?variant={rsid}` | Variant-disease associations (dbSNP rsID) |

Full endpoint and parameter reference (login required): https://api.disgenet.com/doc/swagger

## Parameters
- `source` — e.g. `CURATED` (academic keys are limited to curated sources)
- `min_score` — score threshold (see the score note below)
- `page_number` — 0-based pagination

## Example Calls
```
# Gene-disease for TP53 (gene ID 7157)
/gda/summary?gene_ncbi_id=7157&source=CURATED&min_score=0.3&page_number=0

# Disease-gene for Breast Cancer (UMLS CUI C0006142)
/gda/summary?disease=UMLS_C0006142&page_number=0

# Variant-disease for rs1042522
/vda/summary?variant=rs1042522
```

HTTP 429 responses mean the rate limit was hit; wait before retrying.

## Interpreting results

For a reproducible retrieval, choose gene–disease (GDA) or variant–disease (VDA),
resolve the input identifier, and save source filters, release, evidence rows,
PMIDs, score fields and pagination metadata. Summary rows aggregate evidence;
inspect supporting evidence before making a mechanistic claim.

[Current score guidance](https://support.disgenet.com/support/solutions/articles/202000100283-what-are-the-gda-score-vda-score-disgenet-score-)
removes the former cap at 1. Do not treat the raw DISGENET score as a probability,
clamp it to [0,1], or confuse it with a normalized score. DSI measures disease
specificity and DPI pleiotropy; neither is causal evidence.
