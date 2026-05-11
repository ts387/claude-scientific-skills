# ZINC22 (CartBlanche22 API)

## Base URL
```
https://cartblanche22.docking.org/
```

ZINC22 (current; 230M+ purchasable + multi-billion make-on-demand) is served by the CartBlanche22 query layer. The legacy `zinc.docking.org` endpoint targets ZINC15 and is not actively maintained.

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
- For ZINC15 / drug-like / lead-like compound subsets, the older `zinc.docking.org` endpoint may still resolve but is not the recommended target.
