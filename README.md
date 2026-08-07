# Cross-Statistics Citation Network (CSCN)

CSCN is a directed author-hypergraph dataset for studying how statistical ideas
move within statistics and across neighboring research domains. Unlike an ordinary
author citation graph, a directed hyperedge retains the set-valued structure of a
paper citation: the authors of the cited paper form the tail, and the authors of the
citing paper form the head.

> **Release scope.** This repository currently provides an analysis-ready subgraph
> of 233 authors. The complete raw CSCN corpus is still being updated and extended
> and will be released later.

## Dataset at a glance

| Quantity | Value |
| --- | ---: |
| Authors | 233 |
| Papers represented in the hypergraph | 2,777 |
| Unique paper-citation pairs | 8,691 |
| Processed directed author-hyperedges | 107,551 |
| Maximum processed tail size | 2 |
| Maximum processed head size | 2 |
| Tail communities | 5 |
| Head communities | 4 |
| Weakly connected components | 1 |

All 233 authors are active in the released network. Author identifiers are stable
within this release, and paper identifiers are pseudonymous dataset identifiers.

## Direction and released representation

For every directed hyperedge,

```text
tail = authors of the cited paper
head = authors of the citing paper
```

The direction therefore follows the flow of a citation from the cited author set to
the citing author set. Author sets larger than the model limit are converted into
size-constrained combinations during dataset construction. Consequently, a single
paper-citation pair can produce more than one processed hyperedge.

This repository contains only the resulting processed hyperedges, for which each
side has one or two authors. It does not contain the original large hyperedges,
their pre-processing endpoint counts, expansion flags, or intermediate audit
tables. Semicolon-separated fields preserve multiple authors on a processed side.

## Repository structure

```text
Git-CSCN/
├── data/
│   ├── nodes/          Author metadata and stable node identifiers
│   ├── network/        Processed directed hyperedges in CSV and Parquet formats
│   ├── communities/    Side-specific author communities and summaries
│   └── derived/        Analysis-ready aggregate flow and temporal tables
├── docs/               Field definitions and interpretation notes
├── scripts/            Lightweight release validation
├── dataset_summary.json
├── checksums.sha256
├── LICENSE
├── LICENSE-CODE
├── .gitignore
└── README.md
```

## Complete file inventory

### Repository-level files

| File | Description |
| --- | --- |
| `README.md` | Main introduction, release scope, representation convention, repository guide, construction summary, and usage examples. |
| `dataset_summary.json` | Machine-readable headline statistics, including author, paper, processed-hyperedge, community, and component counts. |
| `checksums.sha256` | SHA-256 fingerprints for every released data file and `dataset_summary.json`; these detect corruption or unintended changes after download or transfer. |
| `LICENSE` | Creative Commons Attribution 4.0 International legal text covering the dataset and documentation. |
| `LICENSE-CODE` | MIT License covering the validation script in `scripts/`. |
| `.gitignore` | Prevents operating-system metadata and local Python cache files from being committed. |

The checksums can be verified from the repository root with:

```bash
shasum -a 256 -c checksums.sha256
```

An `OK` result for every entry means that the checked files are byte-for-byte
identical to this release. The checksum file contains no credentials or private
information.

### `data/nodes/`

| File | Description |
| --- | --- |
| `data/nodes/authors.csv` | One row per author, including stable identifiers, public scholarly identifiers, domains, topics, and network statistics. |
| `data/nodes/authors.parquet` | The same 233 author records in compact, typed Parquet format. |

### `data/network/`

| File | Description |
| --- | --- |
| `data/network/hyperedges.csv` | One row per processed directed author-hyperedge, with cited and citing paper identifiers and both size-constrained author sets. |
| `data/network/hyperedges.parquet` | The same 107,551 processed hyperedge rows in compact, typed Parquet format. |

### `data/communities/`

| File | Description |
| --- | --- |
| `data/communities/author_communities.csv` | Tail- and head-side community assignments for every author. |
| `data/communities/community_summary.csv` | Nine side-specific community summaries: five cited-side and four citing-side communities. |

### `data/derived/`

| File | Description |
| --- | --- |
| `data/derived/tail_to_head_flow.csv` | Aggregate directed flow from each cited-side community (`T1`–`T5`) to each citing-side community (`H1`–`H4`), including row-normalized shares. |
| `data/derived/community_statistics_linkage.csv` | Community-level paper and author coverage describing how each community cites, and is cited by, statistics papers. |
| `data/derived/cross_field_statistics_linkage.csv` | The same directional linkage measures aggregated over biology, computer science, and economics. |
| `data/derived/temporal_tail_to_head_flow.csv` | Tail-to-head community flow in four publication periods, with normalization by the tail source and the head user. |
| `data/derived/temporal_field_asymmetry.csv` | Period-specific citation counts and directional ratios between statistics and each external field. |
| `data/derived/h3_temporal_source_composition.csv` | The changing contribution of tail communities `T1`–`T5` to head community `H3` over time. |

### Documentation and validation

| File | Description |
| --- | --- |
| `docs/DATA_DICTIONARY.md` | Field-by-field definitions, join keys, encodings, units, missing-value conventions, and descriptions of every derived table. |
| `scripts/validate_release.py` | Standard-library checks for required files, node coverage, unique identifiers, endpoint mappings, processed side sizes, community coverage, connectivity, and headline counts. |

CSV is provided for portability. The two largest core tables are also supplied in
Parquet format for faster loading and more compact storage. Detailed definitions are
available in `docs/DATA_DICTIONARY.md`.

## Dataset construction

The subgraph was constructed by harmonizing bibliographic metadata from multiple
scholarly sources, resolving author entities using persistent scholarly identifiers
and bibliographic context, and mapping paper-level citations to canonical author
sets. The released topology uses a fixed author index from 1 to 233. Self-overlap
between the two sides is excluded.

When a selected author set exceeds the model limit, dataset construction converts
it into combinations whose tail and head each contain at most two authors. The
network files expose only these processed model inputs; the source-scale and
intermediate representations are outside this release.

The community files preserve citation-role asymmetry: an author may belong to one
community when acting on the cited side and another when acting on the citing side.
This is an intended feature of the dataset rather than a duplicated assignment.

## Quick start

```python
import pandas as pd

authors = pd.read_csv("data/nodes/authors.csv")
hyperedges = pd.read_parquet("data/network/hyperedges.parquet")
communities = pd.read_csv("data/communities/author_communities.csv")

print(authors.shape)       # (233, 21)
print(hyperedges.shape)    # (107551, 9)
print(communities.shape)   # (233, 7)
```

To validate the release after downloading it:

```bash
python3 scripts/validate_release.py
```

The validator uses only the Python standard library.

## License

The dataset, aggregate tables, metadata, and documentation are released under the
Creative Commons Attribution 4.0 International License; see `LICENSE` for the
official legal text. The validation code under `scripts/` is released under the MIT
License; see `LICENSE-CODE`.

When redistributing or adapting the data, please identify the source as the
**Cross-Statistics Citation Network (CSCN), 233-author subgraph, 2026**, link to the
repository, and indicate whether changes were made.
