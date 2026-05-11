# HMDB (Human Metabolome Database)

## Base URL
```
https://hmdb.ca/
```

HMDB v5.0 (2023-07) covers 220,945 metabolite entries and 8,610 protein sequences for human metabolomics.

## Auth
None required for public web access. **No public REST API** — programmatic API access requires emailing the maintainers (`samackay@ualberta.ca` commercial, `eponine@ualberta.ca` academic).

## Direct Entry URLs

Each metabolite has a stable public entry page that can be fetched directly. Format suffix selects the representation.

```
https://hmdb.ca/metabolites/{HMDB_ID}              # HTML
https://hmdb.ca/metabolites/{HMDB_ID}.xml          # Full XML (130+ fields)
https://hmdb.ca/metabolites/{HMDB_ID}.json         # JSON
https://hmdb.ca/metabolites/{HMDB_ID}.sdf          # 2D structure (SDF)
```

HMDB IDs are 11 characters: `HMDB` + 7-digit zero-padded number (e.g. `HMDB0000001`).

## Example Calls
```
# Full metabolite record (XML) for 1-Methylhistidine
https://hmdb.ca/metabolites/HMDB0000001.xml

# JSON form
https://hmdb.ca/metabolites/HMDB0000001.json

# 2D structure
https://hmdb.ca/metabolites/HMDB0000001.sdf
```

## Search (HTML only)

There is no JSON search endpoint. The web search interface lives at `https://hmdb.ca/spectra/search` and `https://hmdb.ca/structures/search`. Scripted querying requires HTML scraping — prefer the bulk download route for any large-scale work.

## Bulk Downloads
```
https://hmdb.ca/downloads
```

Available archives:

| File | Contents |
|------|----------|
| `hmdb_metabolites.zip` | All metabolite XML records |
| `hmdb_proteins.zip` | Protein/enzyme XML records |
| `structures.zip` | All metabolite structures (SDF) |
| `urine_metabolites.zip`, `serum_metabolites.zip`, `csf_metabolites.zip`, etc. | Specimen-filtered subsets |
| `hmdb_experimental_msms_spectra.zip` | Experimental MS-MS spectra |
| `hmdb_predicted_msms_spectra.zip` | Predicted MS-MS spectra |
| `hmdb_nmr_peak_lists.zip` | NMR peak lists |

Also available in SDF, FASTA, TXT, CSV/TSV depending on dataset.

## Key XML Fields

Identification: `accession`, `secondary_accessions`, `name`, `synonyms`, `chemical_formula`, `average_molecular_weight`, `monoisotopic_molecular_weight`, `smiles`, `inchi`, `inchikey`, `iupac_name`.

Biology: `origin`, `biofluid_locations`, `tissue_locations`, `cellular_locations`, `pathways` (with SMPDB/KEGG IDs), `protein_associations`.

Clinical: `normal_concentrations`, `abnormal_concentrations` (per biofluid, with age/gender), `diseases`, `biomarker` flag.

Spectra: `nmr_spectra`, `ms_spectra`, `ms_ms_spectra`, `predicted_properties`.

Xrefs: `kegg_id`, `pubchem_compound_id`, `chemspider_id`, `chebi_id`, `metlin_id`, `drugbank_id`, `wikipedia_id`, `synthesis_reference`.

## Rate Limits
No documented limits; download archives for large-scale analysis rather than fetching entries one-by-one.

## License & Citation
Free for academic / non-commercial use. Commercial use requires explicit permission. Cite the HMDB paper (Wishart et al., *Nucleic Acids Research*) when using the data.

## Related Databases (same ecosystem)
- **DrugBank** — drugs and pharmaceuticals (separate skill)
- **T3DB** — toxins
- **SMPDB** — small-molecule pathway diagrams (linked from HMDB pathway fields)
- **FooDB** — food components
