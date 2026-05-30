#!/usr/bin/env python3
"""
Phase I — merge expansion_V10_batch.json (11 edges) then
expansion_V10_reparent_manifest.json (2 edge modifications) into the atlas.

Routing (from the `route:` tag in each batch edge's notes):
  - governance_leadership  -> 12_governance_societies.json   (5 edges)
  - direct_training        -> 04_cardiothoracic_vascular.json (1 edge)
  - institutional_parent   -> 15_institutional_hierarchy.json (5 edges, phase_f style)

Discipline:
  - duplicate (source, target, edge_type) check before each insert
  - manifest: confirm live edge matches expected_existing before mutating;
    change only target_node, set new notes, preserve all other fields.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
BATCH_PATH = ROOT / "expansion_V10_batch.json"
MANIFEST_PATH = ROOT / "expansion_V10_reparent_manifest.json"

ROUTE_RE = re.compile(r"route:\s*([0-9A-Za-z_]+)")
ROUTE_TO_FILE = {
    "12_governance_societies": "12_governance_societies.json",
    "04_cardiothoracic_vascular": "04_cardiothoracic_vascular.json",
    "15_institutional_hierarchy": "15_institutional_hierarchy.json",
}


def module_files():
    return [f for f in sorted(ROOT.glob("[0-9][0-9]_*.json"))
            if not (f.name.startswith("00_") or f.name.startswith("99_"))]


def existing_triples():
    triples = set()
    for f in module_files():
        for e in json.loads(f.read_text()):
            triples.add((e["source_node"], e["target_node"], e["edge_type"]))
    return triples


def route_for(edge):
    m = ROUTE_RE.search(edge.get("notes", ""))
    if not m:
        sys.exit(f"ABORT: no route tag in notes for edge "
                 f"{edge['source_node']} -> {edge['target_node']}")
    key = m.group(1)
    if key not in ROUTE_TO_FILE:
        sys.exit(f"ABORT: unknown route {key!r}")
    return ROUTE_TO_FILE[key]


def apply_batch():
    batch = json.loads(BATCH_PATH.read_text())
    triples = existing_triples()

    # Sanity: routing must agree with edge_type contract from the task.
    EXPECT_TYPE = {
        "12_governance_societies.json": "governance_leadership",
        "04_cardiothoracic_vascular.json": "direct_training",
        "15_institutional_hierarchy.json": "institutional_parent",
    }

    by_file = {}
    for e in batch:
        dest = route_for(e)
        if e["edge_type"] != EXPECT_TYPE[dest]:
            sys.exit(f"ABORT: edge_type {e['edge_type']!r} routed to {dest} "
                     f"expecting {EXPECT_TYPE[dest]!r}")
        key = (e["source_node"], e["target_node"], e["edge_type"])
        if key in triples:
            sys.exit(f"ABORT: duplicate triple already present, refusing insert: {key}")
        triples.add(key)
        by_file.setdefault(dest, []).append(e)

    inserted = []
    for fname, new_edges in by_file.items():
        p = ROOT / fname
        edges = json.loads(p.read_text())
        edges.extend(new_edges)
        p.write_text(json.dumps(edges, indent=2))
        json.loads(p.read_text())  # re-parse guard
        for e in new_edges:
            inserted.append((fname, e["source_node"], e["target_node"], e["edge_type"]))

    print("=== Phase I.1 — batch insert ===")
    print(f"Batch edges: {len(batch)} (inserted {len(inserted)})")
    for fname in sorted(by_file):
        print(f"  -> {fname}: {len(by_file[fname])} edge(s)")
        for _, s, t, et in [r for r in inserted if r[0] == fname]:
            print(f"       {et}: {s} -> {t}")
    return len(batch)


def apply_manifest():
    manifest = json.loads(MANIFEST_PATH.read_text())
    assert manifest["manifest_type"] == "edge_modify"
    target_file = ROOT / "15_institutional_hierarchy.json"
    edges = json.loads(target_file.read_text())

    print("\n=== Phase I.2 — reparent manifest ===")
    applied = 0
    for op in manifest["operations"]:
        match = op["match"]
        # locate the unique live edge
        candidates = [
            e for e in edges
            if e["source_node"] == match["source_node"]
            and e["target_node"] == match["target_node"]
            and e["edge_type"] == match["edge_type"]
        ]
        if len(candidates) != 1:
            sys.exit(f"ABORT: expected exactly 1 live edge for match {match}, "
                     f"found {len(candidates)}")
        edge = candidates[0]

        # confirm expected_existing
        for k, v in op["expected_existing"].items():
            if edge.get(k) != v:
                sys.exit(f"ABORT: expected_existing mismatch on {k!r}: "
                         f"live={edge.get(k)!r} expected={v!r} for {match['source_node']}")

        before_target = edge["target_node"]
        before_keys = {k: edge.get(k) for k in op.get("preserve", [])}

        # mutate: target_node + notes only
        edge["target_node"] = op["replace"]["target_node"]
        edge["notes"] = op["notes_set"]

        # verify preserved fields untouched
        for k in op.get("preserve", []):
            if edge.get(k) != before_keys[k]:
                sys.exit(f"ABORT: preserved field {k!r} changed unexpectedly")

        applied += 1
        print(f"  {edge['source_node']}: target {before_target!r} -> "
              f"{edge['target_node']!r}")

    target_file.write_text(json.dumps(edges, indent=2))
    json.loads(target_file.read_text())
    print(f"Operations applied: {applied}")
    return applied


def main():
    n_batch = apply_batch()
    n_ops = apply_manifest()
    print(f"\nPhase I complete: +{n_batch} edges, {n_ops} reparent op(s).")


if __name__ == "__main__":
    main()
