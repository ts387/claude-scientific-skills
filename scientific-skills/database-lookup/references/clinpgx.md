# ClinPGx (Clinical Pharmacogenomics, formerly PharmGKB)

## Base URL
```
https://api.clinpgx.org/v1/data/
```
Note: PharmGKB was consolidated into ClinPGx in July 2025; the legacy host https://api.pharmgkb.org/ redirects here. Use the current base URL above.

## Auth
No API key required for read-only access.

## Key Endpoints

### General search
```
GET https://api.clinpgx.org/v1/search?q={term}&page=0&size=10
```

### Gene data
```
GET /gene?symbol={symbol}
```
Example: `/gene?symbol=CYP2D6`

Response includes: id, symbol, chromosome, hasGuideline, hasClinicalAnnotation, cpicGene

### Drug data
```
GET /drug?name={name}
```
Example: `/drug?name=warfarin`

Response includes: id, name, genericNames, tradeNames, rxNormId, atcCodes

### Clinical annotations (drug-gene interactions)
```
GET /clinicalAnnotation?gene={symbol}&drug={name}&level={level}
```

Evidence levels: `1A`, `1B`, `2A`, `2B`, `3`, `4`

Example:
```
/clinicalAnnotation?gene=CYP2C19&drug=clopidogrel&level=1A
```

Response includes: level, gene, drug, phenotype, significance, variants, url

### CPIC/DPWG guidelines
```
GET /guideline?gene={symbol}&drug={name}&source=CPIC
```

### Pharmacokinetic pathways
```
GET /pathway?drug={name}
```

### Drug labels (FDA, EMA)
```
GET /drugLabel?drug={name}&source=FDA
```

## Rate Limits
Max 2 requests/second; excess requests return HTTP 429. Bulk data via the ClinPGx downloads page.
