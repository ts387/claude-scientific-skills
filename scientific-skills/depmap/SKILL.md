---
name: depmap
description: Query the Cancer Dependency Map (DepMap) for cancer cell line gene dependency scores (CRISPR Chronos), drug sensitivity data, and gene effect profiles. Use for identifying cancer-specific vulnerabilities, synthetic lethal interactions, and validating oncology drug targets.
license: CC-BY-4.0
metadata:
    skill-author: Kuan-lin Huang
---

# DepMap — Cancer Dependency Map

## Overview

The Cancer Dependency Map (DepMap) project, run by the Broad Institute, systematically characterizes genetic dependencies across hundreds of cancer cell lines using genome-wide CRISPR knockout screens (DepMap CRISPR), RNA interference (RNAi), and compound sensitivity assays (PRISM). DepMap data is essential for:
- Identifying which genes are essential for specific cancer types
- Finding cancer-selective dependencies (therapeutic targets)
- Validating oncology drug targets
- Discovering synthetic lethal interactions

**Key resources:**
- DepMap Portal: https://depmap.org/portal/
- DepMap data downloads: https://depmap.org/portal/download/all/
- Python: no official client (the PyPI `depmap` package is unrelated); use the download files below. R users: Bioconductor `depmap` package (ExperimentHub)
- API: https://depmap.org/portal/api/ (the portal's own Swagger API; not a stable public data API and subject to change; scripted access may hit a bot-verification page)

## When to Use This Skill

Use DepMap when:

- **Target validation**: Is a gene essential for survival in cancer cell lines with a specific mutation (e.g., KRAS-mutant)?
- **Biomarker discovery**: What genomic features predict sensitivity to knockout of a gene?
- **Synthetic lethality**: Find genes that are selectively essential when another gene is mutated/deleted
- **Drug sensitivity**: What cell line features predict response to a compound?
- **Pan-cancer essentiality**: Is a gene broadly essential across all cancer types (bad target) or selectively essential?
- **Correlation analysis**: Which pairs of genes have correlated dependency profiles (co-essentiality)?

## Core Concepts

### Dependency Scores

| Score | Range | Meaning |
|-------|-------|---------|
| **Chronos** (CRISPR) | ~ -3 to 0+ | More negative = more essential. Common essential threshold: −1. Pan-essential genes ~−1 to −2 |
| **RNAi DEMETER2** | ~ -3 to 0+ | Similar scale to Chronos |
| **Gene Effect** | normalized | Normalized Chronos; −1 = median effect of common essential genes |

**Key thresholds:**
- Chronos ≤ −0.5: likely dependent
- Chronos ≤ −1: strongly dependent (common essential range)

### Cell Line Annotations

Since the 22Q4 release, cell line metadata is in `Model.csv` (it replaced `sample_info.csv`). Each cell line has:
- `ModelID`: unique identifier (e.g., `ACH-000001`)
- `CellLineName`: human-readable name
- `OncotreePrimaryDisease`: cancer type
- `OncotreeLineage`: broad tissue lineage (e.g., `Lung`, `Myeloid`)
- `OncotreeSubtype`: specific subtype

## Core Capabilities

### 1. Programmatic Access

DepMap does not document a stable public REST API for per-gene dependency scores. The supported programmatic route is to download the release files (CRISPRGeneEffect.csv, Model.csv, Omics*.csv) and analyze them locally, as shown below. Release files are listed on https://depmap.org/portal/download/all/ and each public release is also deposited on Figshare+ (e.g. DepMap 24Q4 Public: https://plus.figshare.com/articles/dataset/DepMap_24Q4_Public/27993248). R users can load the data through the Bioconductor `depmap` package.

### 2. Gene Dependency Scores

Per-gene scores are a column of `CRISPRGeneEffect.csv` (rows = `ModelID`, columns = genes); see `load_depmap_gene_effect()` below and select `df[gene_symbol]`.

### 3. Download-Based Analysis (Recommended)

For large-scale analysis, download DepMap data files and analyze locally:

```python
import pandas as pd
import requests, os

def download_depmap_data(url, output_path):
    """Download a DepMap data file."""
    response = requests.get(url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

# DepMap 24Q4 data files (update version as needed)
FILES = {
    "crispr_gene_effect": "https://figshare.com/ndownloader/files/...",
    # OR download from: https://depmap.org/portal/download/all/
    # Files available:
    # CRISPRGeneEffect.csv - Chronos gene effect scores
    # OmicsExpressionProteinCodingGenesTPMLogp1.csv - mRNA expression
    # OmicsSomaticMutationsMatrixDamaging.csv - mutation binary matrix
    # OmicsCNGene.csv - copy number
    # Model.csv - cell line metadata (replaced sample_info.csv in 22Q4)
}

def load_depmap_gene_effect(filepath="CRISPRGeneEffect.csv"):
    """
    Load DepMap CRISPR gene effect matrix.
    Rows = cell lines (ModelID), Columns = genes (Symbol (EntrezID))
    """
    df = pd.read_csv(filepath, index_col=0)
    # Rename columns to gene symbols only
    df.columns = [col.split(" ")[0] for col in df.columns]
    return df

def load_cell_line_info(filepath="Model.csv"):
    """Load cell line metadata."""
    return pd.read_csv(filepath)
```

### 4. Identifying Selective Dependencies

```python
import numpy as np
import pandas as pd

def find_selective_dependencies(gene_effect_df, cell_line_info, target_gene,
                                 cancer_type=None, threshold=-0.5):
    """Find cell lines selectively dependent on a gene."""

    # Get scores for target gene
    if target_gene not in gene_effect_df.columns:
        return None

    scores = gene_effect_df[target_gene].dropna()
    dependent = scores[scores <= threshold]

    # Add cell line info
    result = pd.DataFrame({
        "ModelID": dependent.index,
        "gene_effect": dependent.values
    }).merge(cell_line_info[["ModelID", "CellLineName", "OncotreePrimaryDisease", "OncotreeLineage"]])

    if cancer_type:
        result = result[result["OncotreePrimaryDisease"].str.contains(cancer_type, case=False, na=False)]

    return result.sort_values("gene_effect")

# Example usage (after loading data)
# df_effect = load_depmap_gene_effect("CRISPRGeneEffect.csv")
# cell_info = load_cell_line_info("Model.csv")
# deps = find_selective_dependencies(df_effect, cell_info, "KRAS", cancer_type="Lung")
```

### 5. Biomarker Analysis (Gene Effect vs. Mutation)

```python
import pandas as pd
from scipy import stats

def biomarker_analysis(gene_effect_df, mutation_df, target_gene, biomarker_gene):
    """
    Test if mutation in biomarker_gene predicts dependency on target_gene.

    Args:
        gene_effect_df: CRISPR gene effect DataFrame
        mutation_df: Binary mutation DataFrame (1 = mutated)
        target_gene: Gene to assess dependency of
        biomarker_gene: Gene whose mutation may predict dependency
    """
    if target_gene not in gene_effect_df.columns or biomarker_gene not in mutation_df.columns:
        return None

    # Align cell lines
    common_lines = gene_effect_df.index.intersection(mutation_df.index)
    scores = gene_effect_df.loc[common_lines, target_gene].dropna()
    mutations = mutation_df.loc[scores.index, biomarker_gene]

    mutated = scores[mutations == 1]
    wt = scores[mutations == 0]

    stat, pval = stats.mannwhitneyu(mutated, wt, alternative='less')

    return {
        "target_gene": target_gene,
        "biomarker_gene": biomarker_gene,
        "n_mutated": len(mutated),
        "n_wt": len(wt),
        "mean_effect_mutated": mutated.mean(),
        "mean_effect_wt": wt.mean(),
        "pval": pval,
        "significant": pval < 0.05
    }
```

### 6. Co-Essentiality Analysis

```python
import pandas as pd

def co_essentiality(gene_effect_df, target_gene, top_n=20):
    """Find genes with most correlated dependency profiles (co-essential partners)."""
    if target_gene not in gene_effect_df.columns:
        return None

    target_scores = gene_effect_df[target_gene].dropna()

    correlations = {}
    for gene in gene_effect_df.columns:
        if gene == target_gene:
            continue
        other_scores = gene_effect_df[gene].dropna()
        common = target_scores.index.intersection(other_scores.index)
        if len(common) < 50:
            continue
        r = target_scores[common].corr(other_scores[common])
        if not pd.isna(r):
            correlations[gene] = r

    corr_series = pd.Series(correlations).sort_values(ascending=False)
    return corr_series.head(top_n)

# Co-essential genes often share biological complexes or pathways
```

## Query Workflows

### Workflow 1: Target Validation for a Cancer Type

1. Download `CRISPRGeneEffect.csv` and `Model.csv`
2. Filter cell lines by cancer type
3. Compute mean gene effect for target gene in cancer vs. all others
4. Calculate selectivity: how specific is the dependency to your cancer type?
5. Cross-reference with mutation, expression, or CNA data as biomarkers

### Workflow 2: Synthetic Lethality Screen

1. Identify cell lines with mutation/deletion in gene of interest (e.g., BRCA1-mutant)
2. Compute gene effect scores for all genes in mutant vs. WT lines
3. Identify genes significantly more essential in mutant lines (synthetic lethal partners)
4. Filter by selectivity and effect size

### Workflow 3: Compound Sensitivity Analysis

1. Download PRISM compound sensitivity data (`primary-screen-replicate-collapsed-logfold-change.csv`) and the matching compound annotations (`primary-screen-replicate-collapsed-treatment-info.csv`)
2. Correlate compound AUC/log2(fold-change) with genomic features
3. Identify predictive biomarkers for compound sensitivity

## DepMap Data Files Reference

| File | Description |
|------|-------------|
| `CRISPRGeneEffect.csv` | CRISPR Chronos gene effect (primary dependency data) |
| `CRISPRGeneEffectUnscaled.csv` | Unscaled CRISPR scores |
| `RNAi_merged.csv` | DEMETER2 RNAi dependency |
| `Model.csv` | Cell line metadata (`ModelID`, `OncotreeLineage`, `OncotreePrimaryDisease`, etc.) |
| `OmicsExpressionProteinCodingGenesTPMLogp1.csv` | mRNA expression |
| `OmicsSomaticMutationsMatrixDamaging.csv` | Damaging somatic mutations (binary) |
| `OmicsCNGene.csv` | Copy number per gene |
| `primary-screen-replicate-collapsed-logfold-change.csv` | PRISM Repurposing primary screen drug sensitivity (log2 fold change) |

Download all files from: https://depmap.org/portal/download/all/

## Best Practices

- **Use Chronos scores** (not DEMETER2) for current CRISPR analyses — better controlled for cutting efficiency
- **Distinguish pan-essential from cancer-selective**: Target genes with low variance (essential in all lines) are poor drug targets
- **Validate with expression data**: A gene not expressed in a cell line will score as non-essential regardless of actual function
- **Use DepMap ID** (`ModelID`) for cell line identification — `CellLineName` can be ambiguous
- **Account for copy number**: Amplified genes may appear essential due to copy number effect (junk DNA hypothesis)
- **Multiple testing correction**: When computing biomarker associations genome-wide, apply FDR correction

## Additional Resources

- **Dependency analysis guide**: `references/dependency_analysis.md` — Chronos score interpretation, selectivity scoring, lineage codes, genome-wide synthetic-lethality screen, and PRISM data loading
- **DepMap Portal**: https://depmap.org/portal/
- **Data downloads**: https://depmap.org/portal/download/all/
- **DepMap paper**: Behan FM et al. (2019) Nature. PMID: 30971826
- **Chronos paper**: Dempster JM et al. (2021) Genome Biology 22:343. PMID: 34930405 — https://doi.org/10.1186/s13059-021-02540-7
- **GitHub**: https://github.com/broadinstitute/depmap-portal
- **Figshare+ (24Q4 release)**: https://plus.figshare.com/articles/dataset/DepMap_24Q4_Public/27993248
