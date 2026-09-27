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
| `/prediction/{uniprot_accession}` | Prediction metadata and current file URLs by UniProt accession |

## Structure File URLs (direct download)

Prefer the URLs returned by `/prediction/{uniprot_accession}` (`pdbUrl`, `cifUrl`, `bcifUrl`, `paeDocUrl`, `msaUrl`, `plddtDocUrl`, and AlphaMissense annotation URLs) instead of hardcoding a version. AlphaFold DB file names are versioned; as of the checked API response for `P00533`, `latestVersion` is `6`.

Current direct-download patterns:
```
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-model_v6.pdb
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-model_v6.cif
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-model_v6.bcif
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-predicted_aligned_error_v6.json
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-confidence_v6.json
https://alphafold.ebi.ac.uk/files/msa/AF-{UNIPROT}-F1-msa_v6.a3m
```

## Example Calls
```
# Get prediction metadata for EGFR
https://alphafold.ebi.ac.uk/api/prediction/P00533

# Download PDB or mmCIF structure from current metadata
https://alphafold.ebi.ac.uk/files/AF-P00533-F1-model_v6.pdb
https://alphafold.ebi.ac.uk/files/AF-P00533-F1-model_v6.cif

# Download PAE (predicted aligned error)
https://alphafold.ebi.ac.uk/files/AF-P00533-F1-predicted_aligned_error_v6.json
```

## Response Format
`/prediction/{accession}` returns a JSON array. Key fields include `modelEntityId`, `latestVersion`, `allVersions`, `globalMetricValue` (mean pLDDT), `sequenceStart`, `sequenceEnd`, `taxId`, `organismScientificName`, `pdbUrl`, `cifUrl`, `bcifUrl`, `paeDocUrl`, `plddtDocUrl`, `msaUrl`, and AlphaMissense annotation URLs when available. `paeImageUrl` was removed (see Deprecation Notice below).

Coordinate files are available as PDB, mmCIF, and binary CIF. Prefer mmCIF/BCIF for large structures. Per-residue confidence is stored in the coordinate file B-factor column and is also available as confidence JSON. PAE is JSON.

Proteins longer than the model size limit may be represented as overlapping fragments (`F1`, `F2`, ...). Preserve fragment identifiers and residue ranges when reporting results.

## Rate Limits
No strict per-request limit is published. For many proteins, use the metadata endpoint to retrieve current URLs and pace requests conservatively. For proteome-scale or all-database retrievals, use AlphaFold DB's FTP/download pages or Google Cloud public dataset instead of looping over individual file URLs. The database contains over 200M monomer predictions, and current downloads also include selected AlphaFold complex predictions. The Google Cloud bucket name remains `public-datasets-deepmind-alphafold-v4` (the bucket name is not versioned with the release).

## Deprecation Notice
The `/prediction/{uniprot}` response schema changed after a 9-month dual-support period that ended on **25 June 2026**: old field names were sunset in favour of renamed ones (`entryId` → `modelEntityId`, `uniprotStart`/`uniprotEnd` → `sequenceStart`/`sequenceEnd`, `uniprotSequence` → `sequence`, `isReviewed` → `isUniProtReviewed`, `isReferenceProteome` → `isUniProtReferenceProteome`), and `paeImageUrl` was removed (the PAE image is no longer served via the API). See https://www.ebi.ac.uk/pdbe/news/breaking-changes-afdb-predictions-api and the schema at https://alphafold.ebi.ac.uk/api-docs.
