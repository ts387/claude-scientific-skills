# Human Cell Atlas (HCA)

## Base URL
```
https://service.azul.data.humancellatlas.org/
```

## Auth
No auth required.

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/index/projects?size={n}` | List/search projects |
| `/index/samples?size={n}` | List/search samples |
| `/index/files?size={n}` | List/search files |
| `/index/summary` | Summary statistics |

List available catalogs with https://service.azul.data.humancellatlas.org/index/catalogs; pass `catalog=<name>` only to pin a specific release.

## Example Calls
```
# List projects
https://service.azul.data.humancellatlas.org/index/projects?size=5

# Summary stats
https://service.azul.data.humancellatlas.org/index/summary
```

Supports JSON filter parameters for organ, species, library construction, etc.

## Response Format
JSON. `hits` array with project/sample/file metadata + pagination.

## Rate Limits
No published limits. Be reasonable.
