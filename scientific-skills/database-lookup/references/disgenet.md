# DisGeNET (Gene-Disease Associations)

## Base URL
```
https://api.disgenet.com/api/v1
```

The legacy `www.disgenet.org/api` (v7 API with email/password token auth) was replaced when DISGENET moved to disgenet.com.

## Auth
**API key required.** Register at https://www.disgenet.com (free academic plan), then copy the API key from your profile page. Send the key itself (no `Bearer` prefix) as the `Authorization` header:
```bash
curl -H "Authorization: $DISGENET_API_KEY" -H "accept: application/json" \
  "https://api.disgenet.com/api/v1/gda/summary?gene_ncbi_id=7157&page_number=0"
```

Load the key from `.env` as `DISGENET_API_KEY`.

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/gda/summary?gene_ncbi_id={id}` (or `gene_symbol=`) | Gene-disease associations for a gene |
| `/gda/summary?disease=UMLS_{cui}` | Gene-disease associations for a disease |
| `/vda/summary?variant={rsid}` | Variant-disease associations (dbSNP rsID) |

Full endpoint and parameter reference (login required): https://api.disgenet.com/doc/swagger

## Parameters
- `source` — e.g. `CURATED` (academic keys are limited to curated sources)
- `min_score` — GDA score threshold (0-1)
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

## Rate Limits
Free academic tier: ~few hundred requests/day. Paid tiers available. HTTP 429 responses mean the limit was hit; wait before retrying.

## Free alternative
If no API key: use **Open Targets** for disease-gene associations.
