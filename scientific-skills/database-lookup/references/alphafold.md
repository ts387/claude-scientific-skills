# AlphaFold DB (Predicted Protein Structures)

## Base URL
```
https://alphafold.ebi.ac.uk/api/
```

## Auth
No auth required.

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/prediction/{uniprot_accession}` | Prediction metadata by UniProt ID |

## Structure File URLs (direct download)
```
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-model_v6.pdb
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-model_v6.cif
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-predicted_aligned_error_v6.json
```

Best practice: do not hardcode the `_v6` suffix — the version increments with each release. Extract download URLs from the `/prediction/{uniprot}` JSON response, preferring the structured file-listing fields (or build the URL from the response's `latestVersion` field). The old prediction-API field names were sunset on 25 June 2026 and `paeImageUrl` was removed (see Deprecation Notice below); check the current schema at https://alphafold.ebi.ac.uk/api-docs before relying on any URL field.

## Example Calls
```
# Get prediction metadata for EGFR
https://alphafold.ebi.ac.uk/api/prediction/P00533

# Download PDB structure
https://alphafold.ebi.ac.uk/files/AF-P00533-F1-model_v6.pdb

# Download PAE (predicted aligned error)
https://alphafold.ebi.ac.uk/files/AF-P00533-F1-predicted_aligned_error_v6.json
```

## Response Format
JSON for metadata. PDB/mmCIF for structures. PAE as JSON matrix.

## Rate Limits
No strict limits. Use FTP/Cloud for bulk downloads (~200M+ structures). The GCS bucket name remains `public-datasets-deepmind-alphafold-v4` (bucket name is not versioned with the release).

## Deprecation Notice
The `/prediction/{uniprot}` response schema changed after a 9-month dual-support period that ended on **25 June 2026**: old field names were sunset in favour of renamed ones (`entryId` → `modelEntityId`, `uniprotStart`/`uniprotEnd` → `sequenceStart`/`sequenceEnd`, `uniprotSequence` → `sequence`, `isReviewed` → `isUniProtReviewed`, `isReferenceProteome` → `isUniProtReferenceProteome`), and `paeImageUrl` was removed (the PAE image is no longer served via the API). See https://www.ebi.ac.uk/pdbe/news/breaking-changes-afdb-predictions-api and the schema at https://alphafold.ebi.ac.uk/api-docs.
