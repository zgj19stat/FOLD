#!/usr/bin/env python3
"""Validate the CSCN-233 release using only the Python standard library."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODES_PATH = ROOT / "data" / "nodes" / "authors.csv"
EDGES_PATH = ROOT / "data" / "network" / "hyperedges.csv"
COMMUNITIES_PATH = ROOT / "data" / "communities" / "author_communities.csv"
SUMMARY_PATH = ROOT / "dataset_summary.json"

EXPECTED_EDGE_FIELDS = [
    "hyperedge_id",
    "citing_paper_id",
    "cited_paper_id",
    "tail_author_ids",
    "head_author_ids",
    "tail_node_indices",
    "head_node_indices",
    "tail_author_count",
    "head_author_count",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def split_values(value: str) -> list[str]:
    return [item for item in value.split(";") if item]


def component_sizes(nodes: set[int], adjacency: dict[int, set[int]]) -> list[int]:
    unseen = set(nodes)
    sizes: list[int] = []
    while unseen:
        start = unseen.pop()
        stack = [start]
        size = 0
        while stack:
            current = stack.pop()
            size += 1
            neighbors = adjacency[current] & unseen
            unseen.difference_update(neighbors)
            stack.extend(neighbors)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def main() -> None:
    required = [
        ROOT / ".gitignore",
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "LICENSE-CODE",
        ROOT / "checksums.sha256",
        ROOT / "docs" / "DATA_DICTIONARY.md",
        NODES_PATH,
        ROOT / "data" / "nodes" / "authors.parquet",
        EDGES_PATH,
        ROOT / "data" / "network" / "hyperedges.parquet",
        COMMUNITIES_PATH,
        ROOT / "data" / "communities" / "community_summary.csv",
        SUMMARY_PATH,
    ]
    required.extend(sorted((ROOT / "data" / "derived").glob("*.csv")))
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    assert not missing, f"Missing release files: {missing}"

    nodes = read_rows(NODES_PATH)
    assert len(nodes) == 233, f"Expected 233 authors, found {len(nodes)}"
    node_by_index = {int(row["node_index"]): row["author_id"] for row in nodes}
    assert sorted(node_by_index) == list(range(1, 234)), "Node indices are not 1..233"
    assert len(set(node_by_index.values())) == 233, "Author IDs are not unique"

    communities = read_rows(COMMUNITIES_PATH)
    assert len(communities) == 233, "Community table does not cover all authors"
    assert {int(row["node_index"]) for row in communities} == set(node_by_index)
    assert {row["tail_community_id"] for row in communities} == {
        "T1", "T2", "T3", "T4", "T5"
    }
    assert {row["head_community_id"] for row in communities} == {
        "H1", "H2", "H3", "H4"
    }

    with EDGES_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == EXPECTED_EDGE_FIELDS, (
            "The network table must expose only processed hyperedge fields"
        )
        edges = list(reader)

    edge_ids: set[str] = set()
    paper_pairs: set[tuple[str, str]] = set()
    papers: set[str] = set()
    active_nodes: set[int] = set()
    cited_incidence: Counter[int] = Counter()
    citing_incidence: Counter[int] = Counter()
    adjacency: dict[int, set[int]] = defaultdict(set)

    for row in edges:
        edge_id = row["hyperedge_id"]
        assert edge_id not in edge_ids, f"Duplicate hyperedge ID: {edge_id}"
        edge_ids.add(edge_id)
        pair = (row["citing_paper_id"], row["cited_paper_id"])
        paper_pairs.add(pair)
        papers.update(pair)

        tail_ids = split_values(row["tail_author_ids"])
        head_ids = split_values(row["head_author_ids"])
        tail_nodes = [int(value) for value in split_values(row["tail_node_indices"])]
        head_nodes = [int(value) for value in split_values(row["head_node_indices"])]
        tail_count = int(row["tail_author_count"])
        head_count = int(row["head_author_count"])

        assert len(tail_ids) == len(tail_nodes) == tail_count
        assert len(head_ids) == len(head_nodes) == head_count
        assert 1 <= tail_count <= 2 and 1 <= head_count <= 2
        assert len(set(tail_nodes)) == tail_count
        assert len(set(head_nodes)) == head_count
        assert not set(tail_nodes) & set(head_nodes), f"Self-overlap in {edge_id}"
        assert [node_by_index[index] for index in tail_nodes] == tail_ids
        assert [node_by_index[index] for index in head_nodes] == head_ids

        endpoints = set(tail_nodes) | set(head_nodes)
        active_nodes.update(endpoints)
        for index in tail_nodes:
            cited_incidence[index] += 1
        for index in head_nodes:
            citing_incidence[index] += 1
        for index in endpoints:
            adjacency[index].update(endpoints - {index})

    assert len(edges) == len(edge_ids) == 107_551
    assert len(paper_pairs) == 8_691
    assert len(papers) == 2_777
    assert active_nodes == set(node_by_index)
    assert component_sizes(set(node_by_index), adjacency) == [233]

    for row in nodes:
        index = int(row["node_index"])
        assert int(row["cited_side_incidence"]) == cited_incidence[index]
        assert int(row["citing_side_incidence"]) == citing_incidence[index]

    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    assert summary["source_hyperedges_included"] is False
    assert summary["author_count"] == len(nodes)
    assert summary["active_author_count"] == len(active_nodes)
    assert summary["paper_count_in_hypergraph"] == len(papers)
    assert summary["unique_paper_citation_pair_count"] == len(paper_pairs)
    assert summary["processed_directed_hyperedge_count"] == len(edges)
    assert summary["maximum_processed_tail_size"] == 2
    assert summary["maximum_processed_head_size"] == 2
    assert summary["tail_community_count"] == 5
    assert summary["head_community_count"] == 4
    assert summary["weak_component_count"] == 1

    print(
        "CSCN release validation passed: "
        f"{len(nodes)} authors, {len(paper_pairs)} paper-citation pairs, "
        f"{len(edges)} processed directed hyperedges."
    )


if __name__ == "__main__":
    main()
