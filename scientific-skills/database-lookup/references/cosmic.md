# COSMIC (Catalogue of Somatic Mutations in Cancer)

## Access Model
COSMIC has **no public query (search/lookup) REST API**. Programmatic access is limited to
authenticated **file downloads**; query the downloaded files locally.

- Download page (lists every file and its scripted-download command): https://cancer.sanger.ac.uk/cosmic/download/cosmic
- Download help: https://cancer.sanger.ac.uk/cosmic/help/file_download

## Auth
**Registration required.** Free academic account or paid commercial license.

Scripted downloads use **HTTP Basic Auth**: base64-encode `email:password` and send it in the
`Authorization` header.
```bash
AUTH=$(echo -n 'you@example.com:yourpassword' | base64)
```

## Scripted Download (two steps)
1. Request the file with the `Authorization: Basic $AUTH` header, using the scripted-download URL
   shown for that file on the download page. The response is JSON containing a short-lived
   signed `url`.
2. Download the file from that signed URL (no auth header needed).

Legacy form for older releases (pre-v98 file layout):
```bash
curl -H "Authorization: Basic $AUTH" \
  "https://cancer.sanger.ac.uk/cosmic/file_download/GRCh38/cosmic/v97/CosmicMutantExport.tsv.gz"
# -> {"url": "<signed URL>"}; then: curl -o CosmicMutantExport.tsv.gz "<signed URL>"
```

File names, paths and release numbers change between releases; copy the current command from
the download page rather than hard-coding it.

## Rate Limits
Not officially published. Signed download URLs expire after a short time; request a fresh one
per download.

## Important
- There are no per-gene / per-mutation JSON endpoints; do not expect `/genes/{symbol}` or
  `/mutations/...` style calls to work
- SFTP access was retired (last SFTP release v85); all downloads are HTTPS
- Commercial use requires a paid license
- For query-style access without downloading, use **Open Targets** or **cBioPortal**; the
  `gget cosmic` tool (see the gget skill) wraps download-then-query-locally
- NLM Clinical Table Search Service offers a limited COSMIC mutation search API:
  https://clinicaltables.nlm.nih.gov/apidoc/cosmic/v3/doc.html
