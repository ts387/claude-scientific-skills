# ZINC22 (CartBlanche22 API)

## Base URL
```
https://cartblanche22.docking.org/
```

ZINC22 (current; 230M+ purchasable + multi-billion make-on-demand) is served by the CartBlanche22 query layer. The legacy REST endpoint at `zinc.docking.org` now serves ZINC20 (ZINC15 remains at `zinc15.docking.org`); both share the legacy API pattern below and are not actively developed.

## Auth
No API key required.

## URL Pattern
```
/{resource}.{format}:param1=value1&param2=value2
```
Format suffix (`.txt`, `.json`) precedes the colon; query parameters follow it. Output is tab-separated by default.

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/substances.txt:zinc_id={id}` | Lookup by ZINC ID (single or comma-separated list) |
| `/smiles.txt:smiles={smi}` | Search by SMILES (exact or analog with `dist`/`adist`) |
| `/catitems.txt:catitem_id={code}` | Lookup by supplier catalog code |
| `/substance/random.txt:count={n}` | Random compound sample (optional `subset=`) |

## Common Parameters

- `output_fields=` — comma-separated list of return fields
- `dist=N` — Tanimoto distance threshold for SMILES similarity (default `0` = exact)
- `adist=N` — alternative distance parameter for broader analog searches
- `count=N` — number of results (random sampling)
- `subset=` — `lead-like`, `drug-like`, `fragment` (random sampling)

## Output Fields

`zinc_id`, `smiles`, `sub_id`, `supplier_code`, `catalogs`, `tranche`

## Example Calls
```
# Lookup by ZINC ID
https://cartblanche22.docking.org/substances.txt:zinc_id=ZINC000000000001&output_fields=zinc_id,smiles

# Multiple ZINC IDs
https://cartblanche22.docking.org/substances.txt:zinc_id=ZINC000000000001,ZINC000000000002&output_fields=zinc_id,smiles,tranche

# Exact SMILES match
https://cartblanche22.docking.org/smiles.txt:smiles=c1ccccc1

# Similarity search (analogs of ibuprofen)
https://cartblanche22.docking.org/smiles.txt:smiles=CC(C)Cc1ccc(cc1)C(C)C(=O)O&dist=5&output_fields=zinc_id,smiles,catalogs

# Random drug-like sample
https://cartblanche22.docking.org/substance/random.txt:count=1000&subset=drug-like&output_fields=zinc_id,smiles,tranche
```

## Tranche Code

Compounds are bucketed into tranches encoding properties as `H##P###M###-phase`:

- `H##` — number of H-bond donors
- `P###` — LogP × 10 (e.g. `P035` = LogP 3.5)
- `M###` — molecular weight in Da (e.g. `M400` = 400 Da)
- `phase` — reactivity classification

Example: `H05P035M400-0` = 5 HBD, LogP 3.5, MW 400, reactivity phase 0.

## 3D Structures for Docking

```
https://files.docking.org/zinc22/
```
Organized by tranche; formats: MOL2, SDF, DB2.GZ (compressed for DOCK).

## Response Format

Tab-separated text (or JSON with `.json` suffix). One row per compound with the requested `output_fields`.

## Rate Limits
No published limits. Be respectful — similarity and substructure searches are expensive. Cache results locally for repeat queries; parallelize file-repository downloads with `aria2c` or parallel `wget`.

## Notes
- ZINC IDs are 15-digit zero-padded after `ZINC` (e.g. `ZINC000000000053`).
- ZINC explicitly disclaims quality guarantees: verify SMILES, stereochemistry, and supplier availability before experimental use.
- For ZINC15/ZINC20 drug-like / lead-like compound subsets, the older `zinc.docking.org` (ZINC20) or `zinc15.docking.org` (ZINC15) endpoints may still resolve but are not the recommended target.

---

# ZINC15 / ZINC20 Database API (Legacy)

## Base URL

```
https://zinc.docking.org
```

`zinc.docking.org` serves ZINC20 (also at `zinc20.docking.org`); ZINC15 is at `https://zinc15.docking.org`.

## Auth

No API key required. Fully open public API.

## URL Pattern

Resources follow a uniform pattern with format specified by file extension:

```
/{resource}.{format}
/{resource}/{id}.{format}
/{resource}/subsets/{subset}.{format}
```

Supported formats: `.json`, `.csv`, `.txt`, `.smi`, `.sdf`, `.mol2`, `.xml`, `.png`

Field selection (return only specific fields):
```
/{resource}.json:field1+field2+field3
```

## Key Endpoints

### Substance lookup by ZINC ID
```
GET /substances/ZINC000000000053.json
```

### Search by name
```
GET /substances.json?preferred_name=aspirin
```

### Search by InChIKey
```
GET /substances.json?inchikey=BSYNRYMUTXBXSQ-UHFFFAOYSA-N
```

### Search by molecular formula
```
GET /substances.json?mol_formula=C9H8O4
```

### Substructure search (SMILES)
```
GET /substances.json?sub_id-matches=c1ccccc1&count=10
```

### Substructure search (SMARTS)
```
GET /substances.json?sub_id-matches-sma=[ND1]&count=10
```

### Similarity search (Tanimoto, ECFP4 fingerprints)

The threshold (e.g., 40 = 40%) is part of the parameter name. Value can be SMILES or a ZINC ID number.
```
GET /substances/?ecfp4_fp-tanimoto-40=c1ccccc1O
GET /substances/?ecfp4_fp-tanimoto-70=ZINC000000000053
```

### Browse subsets

Filter by purchasability, drug status, reactivity, or origin:
```
GET /substances/subsets/fda.json              # FDA-approved drugs
GET /substances/subsets/in-stock.json         # In-stock compounds
GET /substances/subsets/metabolites.json      # Metabolites
GET /substances/subsets/fda+in-stock.json     # Combine subsets with +
```

Key subsets:
- **Purchasability**: `in-stock`, `on-demand`, `for-sale`, `bb` (building blocks)
- **Drug status**: `fda`, `world`, `in-trials`, `in-man`, `in-vivo`, `in-vitro`
- **Origin**: `biogenic`, `metabolites`, `natural-products`, `endogenous`
- **Reactivity**: `anodyne`, `clean`, `standard`, `reactive`

### Substances for a gene target
```
GET /genes/ACHE/substances.json?count=10
```

### Catalogs
```
GET /catalogs.json                            # List all vendor catalogs
GET /catalogs/cmcd/substances.json            # Substances in a catalog
```

### 2D structure image (300x300 PNG)
```
GET /substances/ZINC000000000053.png
```

### Molecule format conversion
```
GET /apps/mol/convert?from=CC(=O)Oc1ccccc1C(=O)O&to=inchikey
```
Returns the InChIKey as plain text. Supports conversions between SMILES, InChI, and InChIKey.

### Batch resolution (POST)

Resolve multiple names, ZINC IDs, or SMILES at once:
```
POST /substances/resolved/
Content-Type: application/x-www-form-urlencoded

paste=aspirin%0Aibuprofen%0AZINC000000000053&identifiers=y&structures=y&names=y&output_format=json
```

## Query Parameters

### Pagination
- `count=N` — results per page (use `count=all` cautiously on large sets)
- `page=N` — page number (1-indexed)

### Sorting
- `sort=mwt` — ascending by field
- `sort=-mwt` — descending (prefix with `-`)
- `sort=no` — disable sorting for faster bulk queries

### Property filters (comparison operators)
- `mwt-le=500` — molecular weight <= 500
- `logp-ge=2` — LogP >= 2
- `hbd-le=5` — H-bond donors <= 5
- Operators: `-le` (<=), `-ge` (>=), `-lt` (<), `-gt` (>), `-eq` (=)

### Searchable substance attributes

Molecular properties: `mwt`, `logp`, `hba`, `hbd`, `tpsa`, `rb` (rotatable bonds), `num_rings`, `num_aromatic_rings`, `num_heavy_atoms`, `num_chiral_centers`, `fractioncsp3`

Identifiers: `zinc_id`, `smiles`, `inchikey`, `mol_formula`, `preferred_name`, `cas_numbers`

Status: `purchasable`, `reactive`, `bb` (building block)

## Example Calls

### Get properties for a compound
```
GET /substances/ZINC000000000053.json:zinc_id+smiles+mwt+logp+hba+hbd+tpsa+mol_formula+preferred_name
```

### FDA drugs sorted by molecular weight
```
GET /substances/subsets/fda.json:zinc_id+preferred_name+mwt?sort=mwt&count=10
```

### Drug-like compounds (Lipinski filters)
```
GET /substances/subsets/for-sale.json?mwt-le=500&logp-le=5&hbd-le=5&hba-le=10&count=20
```

### Find compounds targeting a specific gene
```
GET /genes/EGFR/substances.json:zinc_id+preferred_name+smiles?count=10
```

## Response Format

```json
[
  {
    "zinc_id": "ZINC000000000053",
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "preferred_name": "aspirin",
    "mwt": 180.159,
    "logp": 1.31,
    "hba": 3,
    "hbd": 1,
    "tpsa": 63,
    "mol_formula": "C9H8O4",
    "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N",
    "purchasable": 5
  }
]
```

Responses are JSON arrays. Single-record lookups (by ZINC ID) return a JSON object.

## Rate Limits

No documented rate limits. The API is publicly funded (NIH NIGMS GM71896). Be respectful:
- Use `count=` to limit result sizes
- Use `sort=no` for faster bulk queries
- Similarity and substructure searches are computationally expensive — expect slower responses
- Avoid `count=all` on large result sets

## Special Notes

- ZINC contains **2+ billion** commercially available compounds — always use `count=` to limit results
- ZINC IDs have the format `ZINC000000000053` (15-digit zero-padded after "ZINC")
- The `.smi` format returns SMILES strings, useful for cheminformatics pipelines
- The `.sdf` format returns 3D structures suitable for docking software
- Subsets can be combined with `+` (e.g., `fda+in-stock` = FDA-approved AND in-stock)
- For virtual screening workflows, use tranches (`/tranches/`) to partition by molecular weight and LogP
