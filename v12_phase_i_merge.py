#!/usr/bin/env python3
"""
Phase I (V12) — merge the V12 MIS/institutional expansion into the atlas.

Byte-identical merge logic to v11_phase_i_merge.py. The ONLY changes are config:
the three input paths point at the V12 files, and ROUTE_TO_FILE gains
11_mis_robotic (the V11 map lacked it; two V12 edges route there).

Inputs (all in ROOT):
  - v12_mis_institutional_expansion.json  (16 new edges, multi-type routing)
  - v12_manifest_A.json  (edge_modify_fields: 1 reparent; conformed from v12_edit_manifest.json)
  - v12_manifest_B.json  (edge_semantic_ops: empty)

Differences from v10_phase_i_merge.py:
  - Route map extended with 02_general_surgery_spread and 12_governance_societies.
  - EXPECT_TYPE relaxed: thematic modules accept any edge_type; the only hard
    rule is 15_institutional_hierarchy -> institutional_parent.
  - Two new manifest handlers (edge_modify_fields, edge_semantic_ops) replace the
    single v10 edge_modify reparent handler.

Discipline preserved from v10:
  - duplicate (source, target, edge_type) check before each batch insert.
  - every mutation is guarded by expected_existing and a unique-match assertion;
    preserve[] fields are verified untouched.

Run order: batch insert -> Manifest A -> Manifest B.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
BATCH_PATH = ROOT / "v12_mis_institutional_expansion.json"
MANIFEST_A_PATH = ROOT / "v12_manifest_A.json"
MANIFEST_B_PATH = ROOT / "v12_manifest_B.json"

ROUTE_RE = re.compile(r"route:\s*([0-9A-Za-z_]+)")
ROUTE_TO_FILE = {
    "02_general_surgery_spread": "02_general_surgery_spread.json",
    "11_mis_robotic": "11_mis_robotic.json",
    "12_governance_societies": "12_governance_societies.json",
    "04_cardiothoracic_vascular": "04_cardiothoracic_vascular.json",
    "15_institutional_hierarchy": "15_institutional_hierarchy.json",
}

# Only hard edge_type contract: the institutional-hierarchy module is
# structural-only. Thematic modules may carry mixed edge types.
HARD_TYPE = {"15_institutional_hierarchy.json": "institutional_parent"}


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


def find_unique(edges, match):
    """Return the single live edge matching source/target/edge_type, else abort."""
    candidates = [
        e for e in edges
        if e["source_node"] == match["source_node"]
        and e["target_node"] == match["target_node"]
        and e["edge_type"] == match["edge_type"]
    ]
    if len(candidates) != 1:
        sys.exit(f"ABORT: expected exactly 1 live edge for match {match}, "
                 f"found {len(candidates)}")
    return candidates[0]


def assert_expected(edge, expected, label):
    for k, v in expected.items():
        if edge.get(k) != v:
            sys.exit(f"ABORT: expected_existing mismatch on {k!r}: "
                     f"live={edge.get(k)!r} expected={v!r} ({label})")


def apply_batch():
    batch = json.loads(BATCH_PATH.read_text())
    triples = existing_triples()

    by_file = {}
    for e in batch:
        dest = route_for(e)
        if dest in HARD_TYPE and e["edge_type"] != HARD_TYPE[dest]:
            sys.exit(f"ABORT: edge_type {e['edge_type']!r} routed to {dest} "
                     f"but that module is restricted to {HARD_TYPE[dest]!r}")
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

    print("=== Phase I.1 — V11 batch insert ===")
    print(f"Batch edges: {len(batch)} (inserted {len(inserted)})")
    for fname in sorted(by_file):
        print(f"  -> {fname}: {len(by_file[fname])} edge(s)")
        for _, s, t, et in [r for r in inserted if r[0] == fname]:
            print(f"       {et}: {s} -> {t}")
    return len(batch)


def apply_manifest_a():
    """Manifest A — edge_modify_fields: attribute-only corrections.

    For each op: locate the unique edge by match, assert every expected_existing
    key, apply set{}, and verify preserve[] fields are untouched. No edge-count
    change.
    """
    manifest = json.loads(MANIFEST_A_PATH.read_text())
    assert manifest["manifest_type"] == "edge_modify_fields", \
        f"unexpected manifest_type {manifest['manifest_type']!r}"
    target_file = ROOT / manifest["target_module"]
    edges = json.loads(target_file.read_text())

    print(f"\n=== Phase I.2 — Manifest A ({manifest['manifest_id']}) ===")
    applied = 0
    for op in manifest["operations"]:
        assert op["op"] == "modify_fields", f"unexpected op {op['op']!r} in Manifest A"
        match = op["match"]
        edge = find_unique(edges, match)
        assert_expected(edge, op["expected_existing"], match["source_node"])

        before = {k: edge.get(k) for k in op.get("preserve", [])}
        for k, v in op["set"].items():
            edge[k] = v
        for k in op.get("preserve", []):
            if edge.get(k) != before[k]:
                sys.exit(f"ABORT: preserved field {k!r} changed unexpectedly "
                         f"({match['source_node']})")

        applied += 1
        print(f"  {match['source_node']} -> {match['target_node']}: "
              f"start_year -> {edge['start_year']} "
              f"({len(op['set'])} field(s) set)")

    target_file.write_text(json.dumps(edges, indent=2))
    json.loads(target_file.read_text())
    print(f"Manifest A operations applied: {applied}")
    return applied


def op_delete(edges, op):
    match = op["match"]
    edge = find_unique(edges, match)
    assert_expected(edge, op["expected_existing"], match["source_node"])
    edges.remove(edge)
    print(f"  delete: {match['source_node']} -> {match['target_node']} "
          f"({match['edge_type']})")
    return -1


def op_reverse_retarget(edges, op):
    match = op["match"]
    edge = find_unique(edges, match)
    assert_expected(edge, op["expected_existing"], match["source_node"])
    before = {k: edge.get(k) for k in op.get("preserve", [])}
    for k, v in op["set"].items():
        edge[k] = v
    for k in op.get("preserve", []):
        if edge.get(k) != before[k]:
            sys.exit(f"ABORT: preserved field {k!r} changed unexpectedly "
                     f"({match['source_node']})")
    print(f"  reverse_retarget: {match['source_node']} -> {match['target_node']} "
          f"=> {edge['source_node']} -> {edge['target_node']}")
    return 0


def op_reclassify(edges, op):
    match = op["match"]
    edge = find_unique(edges, match)
    assert_expected(edge, op["expected_existing"], match["source_node"])
    before = {k: edge.get(k) for k in op.get("preserve", [])}
    old_type = edge["edge_type"]
    for k, v in op["set"].items():
        edge[k] = v
    for k in op.get("preserve", []):
        if edge.get(k) != before[k]:
            sys.exit(f"ABORT: preserved field {k!r} changed unexpectedly "
                     f"({match['source_node']})")
    print(f"  reclassify: {match['source_node']} -> {match['target_node']} "
          f"{old_type} => {edge['edge_type']}")
    return 0


SEMANTIC_DISPATCH = {
    "delete": op_delete,
    "reverse_retarget": op_reverse_retarget,
    "reclassify": op_reclassify,
}


def apply_manifest_b():
    """Manifest B — edge_semantic_ops: per-op module-scoped semantic edits.

    Each op carries its own `module`; dispatch on op in {delete, reverse_retarget,
    reclassify}, each guarded by expected_existing. Files are loaded lazily and
    written once per touched module.
    """
    manifest = json.loads(MANIFEST_B_PATH.read_text())
    assert manifest["manifest_type"] == "edge_semantic_ops", \
        f"unexpected manifest_type {manifest['manifest_type']!r}"

    print(f"\n=== Phase I.3 — Manifest B ({manifest['manifest_id']}) ===")
    loaded = {}          # fname -> edges list
    net_delta = 0
    counts = {"delete": 0, "reverse_retarget": 0, "reclassify": 0}

    for op in manifest["operations"]:
        kind = op["op"]
        if kind not in SEMANTIC_DISPATCH:
            sys.exit(f"ABORT: unknown semantic op {kind!r}")
        fname = op["module"]
        if fname not in ROUTE_TO_FILE.values() and not (ROOT / fname).exists():
            sys.exit(f"ABORT: module {fname!r} not found for op {kind}")
        if fname not in loaded:
            loaded[fname] = json.loads((ROOT / fname).read_text())
        net_delta += SEMANTIC_DISPATCH[kind](loaded[fname], op)
        counts[kind] += 1

    for fname, edges in loaded.items():
        p = ROOT / fname
        p.write_text(json.dumps(edges, indent=2))
        json.loads(p.read_text())

    print(f"Manifest B ops: {counts} | net edge delta: {net_delta}")
    return net_delta


def main():
    n_batch = apply_batch()
    n_a = apply_manifest_a()
    delta_b = apply_manifest_b()
    print(f"\nPhase I (V11) complete: +{n_batch} batch edges, "
          f"{n_a} field-correction op(s), {delta_b} net semantic edge delta.")


if __name__ == "__main__":
    main()
