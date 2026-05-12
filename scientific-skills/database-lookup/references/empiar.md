# EMPIAR (Electron Microscopy Public Image Archive)

## Base URL
```
https://www.ebi.ac.uk/empiar/api/
```

Companion archive to EMDB: while EMDB holds processed 3D maps, EMPIAR holds the **raw 2D image data** (and vEM / X-ray tomography reconstructions) that produced them. ~1000+ entries, ~2+ petabytes.

## Auth
No auth required.

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/entry/{EMPIAR_id}` | Full entry metadata (title, authors, imagesets, dataset_size, release_date, cross_references) |
| `/entry/{EMPIAR_id}/` | Trailing slash form (same response) |

Accession format: `EMPIAR-#####` (e.g. `EMPIAR-10009`).

Full API surface (search, browse, statistics) is documented at `https://www.ebi.ac.uk/empiar/api/documentation/` — the per-entry JSON lookup is the most useful programmatic endpoint.

## Example Calls
```
# Full entry metadata
https://www.ebi.ac.uk/empiar/api/entry/EMPIAR-10009

# Entry pages (HTML)
https://www.ebi.ac.uk/empiar/EMPIAR-10009
```

## Response Format

JSON keyed by accession. Top-level fields include:

- `title`, `release_date`, `experiment_type`, `scale`
- `authors[]`, `corresponding_author`, `principal_investigator[]`
- `imagesets[]` — one per image dataset (raw micrographs, gain refs, motion-corrected stacks, particle stacks). Each entry has `name`, `directory`, `category`, `header_format`, `data_format`, `num_images_or_tilt_series`, `frames_per_image`, `voxel_type`, `pixel_width`, `pixel_height`, `details`
- `dataset_size` (total bytes)
- `cross_references` — typically EMDB accessions (`EMD-####`) for the associated processed map
- `biostudies_references`, `idr_references`, `empiar_references`, `workflows`

## Bulk Data Download

EMPIAR entries are large (raw movies, gigabyte-to-terabyte scale). The API is for metadata only — actual image data is fetched separately:

| Method | Address |
|--------|---------|
| **Globus** (preferred for large entries) | endpoint *Shared EMBL-EBI public endpoint*, path `/gridftp/empiar/world_availability/{entry_number}/` |
| **Aspera** (`ascp`) | `emp_ext3@fasp.ebi.ac.uk:/{entry_number}` on port 33001 |
| **HTTP tarball** | streamed `.zip` from the entry page download button |
| **FTP** | `ftp://ftp.ebi.ac.uk/empiar/world_availability/{entry_number}/` — individual files only, no recursive sub-dir |

`{entry_number}` is the EMPIAR ID with the `EMPIAR-` prefix stripped (e.g. `10009`).

Example Aspera CLI:
```
ascp -QT -l 200M -P33001 -i ~/.aspera/connect/etc/asperaweb_id_dsa.openssh \
  emp_ext3@fasp.ebi.ac.uk:/10009 ~/Destination/path/10009
```

For tooling that already speaks the EMPIAR layout, see `ccpem/empiarreader` and the cryoDRGN EMPIAR examples on GitHub.

## Rate Limits
EBI fair-use. Don't hammer the metadata API; for whole-entry data use Globus or Aspera (not the API).

## Cross-Database Workflow
EMPIAR entries typically link to an EMDB entry via `cross_references`. To go raw images → processed map → fitted atomic model, follow `EMPIAR-##### → EMD-#### → PDB ID` through emdb.md and pdb.md respectively.

## Mirrors
PDBj operates a mirror at `https://empiar.pdbj.org/` with the same content and download options — useful for users closer to Asia.
