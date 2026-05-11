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

Best practice: extract download URLs from the `/prediction/{uniprot}` JSON response (`pdbUrl`, `cifUrl`, `bcifUrl`, `paeImageUrl`, `paeDocUrl`) rather than hardcoding the `_v6` suffix — the version increments with each release.

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
Legacy URL fields (`cifUrl`, `bcifUrl`, `pdbUrl`, `paeImageUrl`, `paeDocUrl`) on the `/prediction/{uniprot}` response are scheduled to be sunset on **25 June 2026**. Migrate clients to the structured file-listing fields before that date.
