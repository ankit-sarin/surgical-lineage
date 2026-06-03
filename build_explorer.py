#!/usr/bin/env python3
"""
build_explorer.py — repeatable builder for the Surgical Lineage Atlas explorer.

Reads the current canonical graph + adjudicated node labels, derives the exact
node/link JSON schema that explorer_template.html's JavaScript consumes, and
injects it into a copy of that template to produce a self-contained HTML atlas.

Re-runnable for any future graph version against the same template: the template
is graph-version-agnostic (header stats are computed at runtime from the embedded
data), so only the inputs below change.

Schema derived from the fields the template JS actually reads:
  node  -> {id, type, degree, label_short}
  link  -> {source(index), target(index), edge_type, start_year, module,
            source_name, target_name, temporal_range, confidence,
            evidence_type, evidence_citation, notes}

`module` is not stored on canonical edges, so it is recovered by mapping each
(source, target, edge_type) triple back to the numbered module file it lives in
(the merge pipeline guarantees these triples are unique).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
CANONICAL = ROOT / "surgical_lineage_graph_canonical.json"
LABELS = ROOT / "node_labels_adjudicated.json"
TEMPLATE = ROOT / "explorer_template.html"
OUTPUT = ROOT / "surgical_lineage_atlas_v11.html"
PLACEHOLDER_TAG = '<script type="application/json" id="graph-data">PLACEHOLDER</script>'


def module_files():
    return [f for f in sorted(ROOT.glob("[0-9][0-9]_*.json"))
            if not (f.name.startswith("00_") or f.name.startswith("99_"))]


def build_module_map():
    """Map (source_node, target_node, edge_type) -> module stem (e.g.
    '15_institutional_hierarchy'). Triples are unique across modules."""
    mapping = {}
    for f in module_files():
        stem = f.stem  # filename without .json
        for e in json.loads(f.read_text()):
            key = (e["source_node"], e["target_node"], e["edge_type"])
            if key in mapping and mapping[key] != stem:
                sys.exit(f"ABORT: triple {key} appears in both "
                         f"{mapping[key]} and {stem}")
            mapping[key] = stem
    return mapping


def load_label_index():
    """id -> usable short label (empty/stub entries fall back to the node id)."""
    idx = {}
    for entry in json.loads(LABELS.read_text()):
        short = (entry.get("label_short") or "").strip()
        if short:
            idx[entry["id"]] = short
    return idx


def build_graph():
    edges = json.loads(CANONICAL.read_text())
    module_map = build_module_map()
    label_idx = load_label_index()

    # ── Build the unique node list with type + stable index ──
    node_index = {}      # id -> index
    node_type = {}       # id -> type
    nodes_order = []     # ids in first-seen order
    for e in edges:
        for nid, ntype in ((e["source_node"], e["source_node_type"]),
                            (e["target_node"], e["target_node_type"])):
            if nid not in node_index:
                node_index[nid] = len(nodes_order)
                node_type[nid] = ntype
                nodes_order.append(nid)

    # ── Degree per node (incidence count over edges) ──
    degree = {nid: 0 for nid in nodes_order}
    for e in edges:
        degree[e["source_node"]] += 1
        degree[e["target_node"]] += 1

    nodes = [{
        "id": nid,
        "type": node_type[nid],
        "degree": degree[nid],
        "label_short": label_idx.get(nid, nid),  # fallback to id when empty/stub
    } for nid in nodes_order]

    # ── Links: indices for source/target + the fields the JS reads ──
    links = []
    for e in edges:
        key = (e["source_node"], e["target_node"], e["edge_type"])
        links.append({
            "source": node_index[e["source_node"]],
            "target": node_index[e["target_node"]],
            "edge_type": e["edge_type"],
            "start_year": e.get("start_year"),
            "module": module_map.get(key, ""),
            "source_name": e["source_node"],
            "target_name": e["target_node"],
            "temporal_range": e.get("temporal_range", ""),
            "confidence": e.get("confidence", ""),
            "evidence_type": e.get("evidence_type", ""),
            "evidence_citation": e.get("evidence_citation", ""),
            "notes": e.get("notes", ""),
        })

    return {"nodes": nodes, "links": links}


def main():
    ap = argparse.ArgumentParser(description="Build the Surgical Lineage Atlas explorer.")
    ap.add_argument("--version", default=None,
                    help="Version tag; output is surgical_lineage_atlas_<version>.html. "
                         "Omit to keep the legacy default output name.")
    args = ap.parse_args()
    output = ROOT / f"surgical_lineage_atlas_{args.version}.html" if args.version else OUTPUT

    template = TEMPLATE.read_text()
    if PLACEHOLDER_TAG not in template:
        sys.exit("ABORT: template is missing the single-encoded PLACEHOLDER embed; "
                 "explorer_template.html must retain it verbatim.")

    graph = build_graph()
    # Single-encoded JSON embed (template reads it via JSON.parse of textContent).
    payload = json.dumps(graph, ensure_ascii=False)
    injected = (
        '<script type="application/json" id="graph-data">'
        + payload
        + '</script>'
    )
    html = template.replace(PLACEHOLDER_TAG, injected)
    output.write_text(html)

    type_counts = {}
    for n in graph["nodes"]:
        type_counts[n["type"]] = type_counts.get(n["type"], 0) + 1
    ip = sum(1 for l in graph["links"] if l["edge_type"] == "institutional_parent")
    stubbed_fallbacks = sum(1 for n in graph["nodes"] if n["label_short"] == n["id"])

    print("=== build_explorer.py ===")
    print(f"Template : {TEMPLATE.name}")
    print(f"Output   : {output.name}")
    print(f"Nodes    : {len(graph['nodes'])} "
          f"({', '.join(f'{k}={v}' for k, v in sorted(type_counts.items()))})")
    print(f"Links    : {len(graph['links'])} (institutional_parent={ip})")
    print(f"Labels   : {len(graph['nodes']) - stubbed_fallbacks} adjudicated, "
          f"{stubbed_fallbacks} id-fallback")
    print("Build OK.")


if __name__ == "__main__":
    main()
