# ClinVar API Reference

## Base URLs
- **NCBI E-utilities**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils`
- **ClinVar web API (VCV)**: `https://www.ncbi.nlm.nih.gov/clinvar`
- **NCBI Variation Services**: `https://api.ncbi.nlm.nih.gov/variation/v0`

## Authentication
- E-utilities: No key required, but **strongly recommended**. Register at https://www.ncbi.nlm.nih.gov/account/ to get an `api_key`.
- Without key: 3 requests/second. With key: 10 requests/second.
- Append `&api_key=YOUR_KEY` to all E-utility requests.

## Rate Limits
- Without API key: 3 req/sec
- With API key: 10 req/sec

## Key Endpoints

### 1. Search ClinVar (esearch)
```
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term={query}&retmode=json
```
Example — search for BRCA1 pathogenic variants:
```
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=BRCA1[gene]+AND+pathogenic[clinical_significance]&retmode=json&retmax=10
```
Returns JSON with `idlist` of ClinVar Variation IDs.

### 2. Fetch ClinVar Records (esummary)
```
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id={id_list}&retmode=json
```
Example:
```
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id=37088,37087&retmode=json
```
Returns JSON with germline / somatic clinical-impact / oncogenicity classifications (each with conditions and review status), variant name, and gene. Since January 2024 the single `clinical_significance` field is split into these three objects.

### 3. Full Record (efetch)
```
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=clinvar&id={id}&rettype=vcv&is_variationid&retmode=xml
```
Note: ClinVar efetch returns **XML only** (no JSON for efetch).

### 4. Variation Services API — SPDI/HGVS Lookup
Variation Services has no ClinVar-specific route. Normalize the variant, map it to an rsID, then read the ClinVar annotations from the RefSNP record:
```
GET https://api.ncbi.nlm.nih.gov/variation/v0/hgvs/{hgvs_expression}/contextuals   # HGVS -> SPDI
GET https://api.ncbi.nlm.nih.gov/variation/v0/spdi/{spdi_expression}/rsids        # SPDI -> rsIDs
GET https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{rsid}                       # RefSNP JSON (clinical annotations under primary_snapshot_data.allele_annotations[].clinical)
```
Example:
```
GET https://api.ncbi.nlm.nih.gov/variation/v0/hgvs/NM_007294.4%3Ac.5266dupC/contextuals
```
For a direct HGVS -> ClinVar lookup, esearch (section 1) with the HGVS expression as the term is simpler.

### 5. ClinVar VCV/RCV Direct Access
```
GET https://www.ncbi.nlm.nih.gov/clinvar/variation/{variation_id}/?redir=vcv
```
This returns HTML. For programmatic access, use E-utilities or the Variation Services API.

## Useful Search Qualifiers
- `[gene]` — gene symbol (e.g., `BRCA1[gene]`)
- `[clinical_significance]` — pathogenic, likely_pathogenic, benign, uncertain_significance
- `[molecular_consequence]` — missense, nonsense, frameshift, etc.
- `[review_status]` — criteria_provided_single_submitter, reviewed_by_expert_panel, etc.
- `[condition]` — disease name

## Response Format
- esearch/esummary: JSON (with `retmode=json`)
- efetch: XML only for ClinVar
- Variation Services: JSON

## esummary Response Key Fields
```json
{
  "result": {
    "37088": {
      "uid": "37088",
      "title": "NM_007294.4(BRCA1):c.5266dupC (p.Gln1756Profs*74)",
      "germline_classification": {
        "description": "Pathogenic",
        "review_status": "reviewed by expert panel",
        "trait_set": [{"trait_name": "Hereditary breast and ovarian cancer syndrome"}]
      },
      "clinical_impact_classification": {...},
      "oncogenicity_classification": {...},
      "genes": [{"symbol": "BRCA1", "geneid": 672}],
      "variation_set": [...]
    }
  }
}
```

## Notes
- Combine esearch + esummary for search-then-fetch workflows.
- For bulk downloads, use ClinVar FTP: https://ftp.ncbi.nlm.nih.gov/pub/clinvar/
