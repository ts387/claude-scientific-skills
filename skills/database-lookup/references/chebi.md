# ChEBI (Chemical Entities of Biological Interest) API Reference

## Base URLs
- **OLS (Ontology Lookup Service) API**: `https://www.ebi.ac.uk/ols4/api`
- **ChEBI REST API (ChEBI 2.0)**: `https://www.ebi.ac.uk/chebi/backend/api/public/` (interactive docs: https://www.ebi.ac.uk/chebi/backend/api/docs/)
- **ChEBI website**: entity pages at `https://www.ebi.ac.uk/chebi`
- **Legacy SOAP web services** (`https://www.ebi.ac.uk/webservices/chebi/2.0/...`): retired on 1 September 2025; do not use.

## Authentication
None required. All endpoints are public.

## Rate Limits
No published hard limits. EBI general guidance: reasonable usage.

## Important Note
Since the ChEBI 2.0 relaunch (2025), ChEBI provides its own **REST/JSON API**; the old SOAP web services were retired on 1 September 2025. The **EBI OLS4 API**, which indexes ChEBI as an ontology, remains a convenient REST alternative for ontology lookups.

---

## OLS4 API Endpoints (Recommended for REST/JSON)

### 1. Search ChEBI Terms
```
GET https://www.ebi.ac.uk/ols4/api/search?q={query}&ontology=chebi
```
Example:
```
GET https://www.ebi.ac.uk/ols4/api/search?q=aspirin&ontology=chebi
```
Returns JSON with matching ChEBI terms, IDs, definitions, synonyms.

### 2. Lookup by ChEBI ID
```
GET https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http://purl.obolibrary.org/obo/CHEBI_{id}
```
Example:
```
GET https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http://purl.obolibrary.org/obo/CHEBI_15365
```
Returns full term details: name, definition, synonyms, xrefs, relationships.

### 3. Get Term by Short Form
```
GET https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FCHEBI_{id}
```
(Double-encoded IRI in path.)

### 4. Term Hierarchy — Parents
```
GET https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FCHEBI_{id}/parents
```

### 5. Term Hierarchy — Children
```
GET https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FCHEBI_{id}/children
```

### 6. Ontology Metadata
```
GET https://www.ebi.ac.uk/ols4/api/ontologies/chebi
```

## OLS Search Response Format
```json
{
  "response": {
    "numFound": 5,
    "docs": [
      {
        "id": "chebi:15365",
        "iri": "http://purl.obolibrary.org/obo/CHEBI_15365",
        "label": "aspirin",
        "description": ["A member of the class of benzoic acids..."],
        "short_form": "CHEBI_15365",
        "obo_id": "CHEBI:15365",
        "ontology_name": "chebi",
        "type": "class"
      }
    ]
  }
}
```

## ChEBI REST API (ChEBI 2.0)
For chemical-specific data (formula, mass, structure, InChI, SMILES, cross-references), use ChEBI's own REST API:
- Base: `https://www.ebi.ac.uk/chebi/backend/api/public/`
- Free-text search: `es_search/`
- Single compound record: `compound/{CHEBI:id}/` (e.g. `compound/CHEBI:15365/`)
- Ontology parent/child routes are also available.
- Check exact paths and query parameters in the interactive docs: https://www.ebi.ac.uk/chebi/backend/api/docs/

The legacy SOAP service (`getCompleteEntity`, `getLiteEntity`, etc. via `webservices/chebi/2.0/webservice?wsdl`) was retired on 1 September 2025; clients that wrap it (e.g. older `bioservices` `ChEBI()` calls) need to migrate to the REST API.

## Notes
- For programmatic REST access, OLS4 is the easiest path.
- For chemical data and structure searches, use the ChEBI REST API (see its docs for the available search routes); the SOAP service no longer exists.
- ChEBI IDs are numeric (e.g., 15365) but referenced as "CHEBI:15365" in OBO format.
- PubChem and UniChem can cross-reference ChEBI IDs to other chemical databases.
