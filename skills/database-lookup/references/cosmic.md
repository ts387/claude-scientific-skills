# COSMIC — Catalogue of Somatic Mutations in Cancer

Use the [official COSMIC site](https://cancer.sanger.ac.uk/cosmic) to search genes,
mutations, tissues and Cancer Gene Census records. Programmatic bulk access is
through the [licensed download service](https://cancer.sanger.ac.uk/cosmic/help/file_download).
A COSMIC account and acceptance of the applicable data licence are required;
commercial access has separate licensing terms.

## Access Model
COSMIC has **no public query (search/lookup) REST API**. Programmatic access is limited to
authenticated **file downloads**; query the downloaded files locally.

- Download page (lists every file and its scripted-download command): https://cancer.sanger.ac.uk/cosmic/download/cosmic
- Download help: https://cancer.sanger.ac.uk/cosmic/help/file_download

Workflow:
1. Sign in through COSMIC and select the dataset, release and genome assembly.
2. Use the download instructions supplied for that release/account (see
   Scripted Download below). If the service supplies a temporary signed URL,
   download it promptly and keep it out of logs and published artifacts.
3. Record the release, file name, checksum, assembly and selected columns.
4. Filter locally by gene, tissue or variant; preserve sample identifiers and
   distinguish mutation counts from numbers of tested samples.

## Scripted Download (two steps)
Scripted downloads use **HTTP Basic Auth**: base64-encode `email:password` and send it in the
`Authorization` header.
```bash
AUTH=$(echo -n 'you@example.com:yourpassword' | base64)
```

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
the download page rather than hard-coding it. Authenticated downloads were not executed during
this review; consult the signed-in official instructions for exact routes.

## Rate Limits
Not officially published. Signed download URLs expire after a short time; request a fresh one
per download.

## Important
- No current public documentation was found supporting a generic `/cosmic/api/v1`
  mutation-search API or a JWT `/auth/login` workflow; those recipes have been removed. There
  are no per-gene / per-mutation JSON endpoints; do not expect `/genes/{symbol}` or
  `/mutations/...` style calls to work
- SFTP access was retired (last SFTP release v85); all downloads are HTTPS
- For query-style access without downloading, use **Open Targets** or **cBioPortal**; the
  `gget cosmic` tool (see the gget skill) wraps download-then-query-locally
- NLM Clinical Table Search Service offers a limited COSMIC mutation search API:
  https://clinicaltables.nlm.nih.gov/apidoc/cosmic/v3/doc.html

COSMIC catalogue inclusion is evidence of observation in a cancer sample, not
proof of driver status, pathogenicity or response to a drug.
