---
name: primekg
description: Query the Precision Medicine Knowledge Graph (PrimeKG) for multiscale biological data including genes, drugs, diseases, phenotypes, and more.
license: Unknown
metadata:
    skill-author: K-Dense Inc. (PrimeKG original from Harvard MIMS)
---

# PrimeKG Knowledge Graph Skill

## Overview

PrimeKG is a precision medicine knowledge graph that integrates over 20 primary databases and high-quality scientific literature into a single resource. It contains over 100,000 nodes and 4 million edges across 30 relationship types, including drug-target, disease-gene, and phenotype-disease associations.

**Key capabilities:**
- Search for nodes (genes, proteins, drugs, diseases, phenotypes)
- Retrieve direct neighbors (associated entities and clinical evidence)
- Analyze local disease context (related genes, drugs, phenotypes)
- Check for direct edges between two nodes, e.g. a drug and a disease (`find_paths`; only depth-1 edges are implemented, so `max_depth` > 1 returns the same result and multi-hop path search is not available)

**Data access:** Programmatic access via `scripts/query_primekg.py`. Set `PRIMEKG_DATA_PATH` to your local copy of `kg.csv` (download from Harvard Dataverse, https://doi.org/10.7910/DVN/IXA7BM); defaults to `data/kg.csv` inside the skill directory.

## When to Use This Skill

This skill should be used when:

- **Knowledge-based drug discovery:** Identifying targets and mechanisms for diseases.
- **Drug repurposing:** Finding existing drugs that might have evidence for new indications.
- **Phenotype analysis:** Understanding how symptoms/phenotypes relate to diseases and genes.
- **Multiscale biology:** Bridging the gap between molecular targets (genes) and clinical outcomes (diseases).
- **Network pharmacology:** Investigating the broader network effects of drug-target interactions.

## Core Workflow

### 1. Search for Entities

Find identifiers for genes, drugs, or diseases.

```python
from scripts.query_primekg import search_nodes

# Search for Alzheimer's disease nodes
results = search_nodes("Alzheimer", node_type="disease")
# Returns e.g.: [{"id": "<MONDO-derived numeric id>", "type": "disease", "name": "Alzheimer disease", "source": "MONDO"}, ...]
# Disease ids are MONDO-derived numbers, not EFO ids; always take them from search_nodes.
```

### 2. Get Neighbors (Direct Associations)

Retrieve all connected nodes and relationship types.

```python
from scripts.query_primekg import get_neighbors

# Get all neighbors of a specific disease ID (taken from search_nodes above)
disease_id = results[0]["id"]
neighbors = get_neighbors(disease_id)
# Returns: List of neighbors like {"neighbor_name": "APOE", "relation": "disease_protein", ...}
```

### 3. Analyze Disease Context

A high-level function to summarize associations for a disease.

```python
from scripts.query_primekg import get_disease_context

# Comprehensive summary for a disease
context = get_disease_context("Alzheimer's disease")
# Access: context['associated_genes'], context['associated_drugs'], context['phenotypes']
```

### 4. Find Direct Paths Between Two Nodes

Check whether two nodes (for example, a drug and a disease) share a direct edge.

```python
from scripts.query_primekg import search_nodes, find_paths

drug_id = search_nodes("Donepezil", node_type="drug")[0]["id"]
disease_id = search_nodes("Alzheimer", node_type="disease")[0]["id"]

paths = find_paths(drug_id, disease_id)
# Returns: list of paths; each path is a one-element list holding the raw edge row
# (relation, display_relation, x_id, x_name, y_id, y_name, ...).
# Only direct (depth-1) edges are returned; multi-hop search is not yet implemented.
```

## Relationship Types in PrimeKG

The graph contains several key relationship types including:
- `protein_protein`: Physical PPIs
- `drug_protein`: Drug target/enzyme/transporter/carrier associations
- `disease_protein`: Disease-gene associations
- `indication`, `contraindication`, `off-label use`: Drug-disease relationships
- `disease_phenotype_positive` / `disease_phenotype_negative`: Clinical signs and symptoms
- `drug_effect`: Drug side effects

## Best Practices

1. **Use specific IDs:** When using `get_neighbors`, ensure you have the correct ID from `search_nodes`.
2. **Context first:** Use `get_disease_context` for a broad overview before diving into specific genes or drugs.
3. **Filter relationships:** Use the `relation_type` filter in `get_neighbors` to focus on specific evidence (e.g., only `drug_protein`).
4. **Multiscale integration:** Combine with the `database-lookup` skill (Open Targets) for deeper genetic evidence or the `paper-lookup` skill (Semantic Scholar) for the latest literature context.

## Resources

### Scripts
- `scripts/query_primekg.py`: Core functions for searching and querying the knowledge graph.

### Data Path
- Data: set `PRIMEKG_DATA_PATH` to the location of `kg.csv` downloaded from Harvard Dataverse (https://doi.org/10.7910/DVN/IXA7BM); defaults to `data/kg.csv` inside the skill directory.
- Total nodes: ~129,000
- Total edges: ~4,000,000
- Database: CSV-based, optimized for pandas querying.
