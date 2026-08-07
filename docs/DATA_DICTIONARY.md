# CSCN data dictionary

## General conventions

- `node_index` is a one-based integer in `1, ..., 233` and is stable within this
  release.
- `author_id`, `citing_paper_id`, and `cited_paper_id` are stable pseudonymous
  identifiers used to join the released tables.
- Lists inside hyperedge CSV cells use semicolons. The `aliases` field is a JSON
  array.
- Missing public scholarly identifiers or affiliations are stored as empty values.
- Fields ending in `_share` or `_share_value` are proportions on the `[0, 1]` scale.
- In the directed hypergraph, `tail` denotes cited-paper authors and `head` denotes
  citing-paper authors.

## Released hyperedge representation

The network tables contain only processed, size-constrained hyperedges. Each
released tail and head contains one or two authors. When an author set is larger
than this during construction, it is converted into model-compatible combinations;
a paper-citation pair can therefore correspond to multiple released rows.

The package does not include the original large hyperedges, original-side author
counts, expansion flags, or intermediate processing tables.

## `data/nodes/`

### `authors.csv` and `authors.parquet`

Both files contain the same 233 author rows.

| Field | Meaning |
| --- | --- |
| `node_index` | One-based node index used by the hyperedge table. |
| `author_id` | Stable CSCN author identifier. |
| `display_name` | Canonical author name for display. |
| `aliases` | JSON array of observed author-name variants. |
| `orcid` | Public ORCID URL when available. |
| `openalex_author_id` | Public OpenAlex author URL when available. |
| `primary_affiliation` | Representative affiliation from the harmonized metadata. |
| `domains` | Semicolon-separated represented research domains. |
| `primary_domain` | Primary domain used for descriptive analysis. |
| `network_paper_count` | Number of represented papers associated with the author. |
| `*_domain_paper_count` | Author paper count in the named domain. |
| `internal_citations_received` | Citation incidence received from authors in the selected network. |
| `internal_citations_made` | Citation incidence made to authors in the selected network. |
| `cited_side_incidence` | Number of processed hyperedge rows containing the author on the tail. |
| `citing_side_incidence` | Number of processed hyperedge rows containing the author on the head. |
| `research_topic` | Machine-readable research-topic code. |
| `research_topic_label` | Human-readable research-topic label. |
| `research_topic_confidence` | Relative confidence of the topic assignment. |

## `data/network/`

### `hyperedges.csv` and `hyperedges.parquet`

Both files contain the same 107,551 processed directed author-hyperedge rows.

| Field | Meaning |
| --- | --- |
| `hyperedge_id` | Unique released hyperedge identifier. |
| `citing_paper_id` | Pseudonymous identifier of the citing paper. |
| `cited_paper_id` | Pseudonymous identifier of the cited paper. |
| `tail_author_ids` | Semicolon-separated cited-paper author identifiers. |
| `head_author_ids` | Semicolon-separated citing-paper author identifiers. |
| `tail_node_indices` | Node indices corresponding to `tail_author_ids`, in the same order. |
| `head_node_indices` | Node indices corresponding to `head_author_ids`, in the same order. |
| `tail_author_count` | Number of authors on the processed tail (`1` or `2`). |
| `head_author_count` | Number of authors on the processed head (`1` or `2`). |

There are 8,691 distinct `(citing_paper_id, cited_paper_id)` pairs. Multiple
processed hyperedges can share a paper pair because a size-constrained author-level
representation can contain multiple endpoint combinations. No author occurs on both
sides of a released hyperedge.

## `data/communities/`

### `author_communities.csv`

One row per author. `tail_community_id` takes values `T1`–`T5`, while
`head_community_id` takes values `H1`–`H4`. The associated label fields provide
interpretable research directions. The two assignments describe different citation
roles and need not be identical.

### `community_summary.csv`

One row per side-specific community. It records community size, dominant domain,
research-topic composition, and representative high-incidence authors. Colon- and
semicolon-delimited count fields provide compact category summaries.

## `data/derived/`

These tables are aggregate views of the released processed subgraph and its
community assignments.

| File | Contents |
| --- | --- |
| `tail_to_head_flow.csv` | Weighted flow from each tail community to each head community, with row-normalized shares. |
| `community_statistics_linkage.csv` | For every side-specific community, paper and author coverage of citation links to statistics. |
| `cross_field_statistics_linkage.csv` | The same linkage summary aggregated over biology, computer science, and economics. |
| `temporal_tail_to_head_flow.csv` | Period-specific community flow with normalization by tail source and head user. |
| `temporal_field_asymmetry.csv` | Period-specific citation counts and ratios between statistics and external fields. |
| `h3_temporal_source_composition.csv` | Temporal composition of the sources entering head community H3. |

Count columns report papers, authors, or weighted citation flow as named. The value
`inf` in a directional ratio denotes a positive numerator and a zero denominator.
