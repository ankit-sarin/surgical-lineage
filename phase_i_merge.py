#!/usr/bin/env python3
"""
Unified Phase I — config-driven merge of an expansion batch + manifests into the atlas.

Merge logic is preserved VERBATIM from v12_phase_i_merge.py:
  - route each batch edge to its module by the `route:` tag in notes,
  - pre-insert duplicate (source, target, edge_type) check,
  - Manifest A `edge_modify_fields` (modify_fields) handler,
  - Manifest B `edge_semantic_ops` (delete / reverse_retarget / reclassify) handler,
  every mutation guarded by expected_existing + a unique-match assertion, preserve[]
  fields verified untouched.

The ONLY behavioural differences from v12_phase_i_merge.py:
  - the route map + edge-type contract are read from --config instead of being hardcoded
    module-level constants (adding a destination is now a one-line config edit),
  - inputs and version come from CLI args,
  - a merge_run_<version>.json record is emitted (pre-counts + derived delta + descriptive
    fields) so phase_h can gate on pre+delta instead of a hardcoded baseline.

Run order (unchanged): batch insert -> Manifest A -> Manifest B.
"""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

import jsonschema

ROUTE_RE = re.compile(r"route:\s*([0-9A-Za-z_]+)")


# --------------------------------------------------------------------------- config / paths
def load_config(config_path):
    cfg = json.loads(Path(config_path).read_text())
    base = Path(config_path).resolve().parent
    cfg["_base"] = base
    cfg["_modules_dir"] = (base / cfg["paths"]["modules_dir"]).resolve()
    cfg["_canonical"] = (base / cfg["paths"]["canonical"]).resolve()
    return cfg


def sha256_file(path):
    """Full 64-char hex digest of a file, or None if it does not exist."""
    p = Path(path)
    if not p.exists():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --------------------------------------------------------------------------- manifest pre-flight
MANIFEST_SCHEMA_NAME = "00_manifest_schema.json"


def validate_manifests(base, manifest_paths):
    """T1.3 — validate every manifest against 00_manifest_schema.json BEFORE any module is
    read or mutated, and exit non-zero listing every violation found.

    V17-B2 lost two runs to dispatch-key defects (a missing op, a missing module) that were
    only discovered mid-merge, one abort at a time, after the batch had already been written
    to disk. Failing here means the modules are never touched.
    """
    schema_path = Path(base) / MANIFEST_SCHEMA_NAME
    if not schema_path.exists():
        sys.exit(f"ABORT: manifest schema not found: {schema_path}")
    schema = json.loads(schema_path.read_text())
    validator = jsonschema.Draft7Validator(schema)

    violations = []
    for label, path in manifest_paths:
        try:
            manifest = json.loads(Path(path).read_text())
        except (OSError, json.JSONDecodeError) as exc:
            violations.append(f"  {label} ({path}): unreadable / invalid JSON — {exc}")
            continue
        for err in sorted(validator.iter_errors(manifest), key=lambda e: list(e.absolute_path)):
            loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
            violations.append(f"  {label} at {loc}: {err.message}")

    print("=== Phase I.0 — manifest pre-flight ===")
    if violations:
        print(f"FAILED: {len(violations)} violation(s); no module was read or modified.")
        for v in violations:
            print(v)
        sys.exit(1)
    for label, path in manifest_paths:
        print(f"  OK: {label} validates against {MANIFEST_SCHEMA_NAME} ({Path(path).name})")


def module_files(modules_dir):
    """Same selection rule as v12: numbered modules, excluding 00_/99_."""
    return [f for f in sorted(modules_dir.glob("[0-9][0-9]_*.json"))
            if not (f.name.startswith("00_") or f.name.startswith("99_"))]


def all_edges(files):
    edges = []
    for f in files:
        edges.extend(json.loads(f.read_text()))
    return edges


def existing_triples(files):
    return {(e["source_node"], e["target_node"], e["edge_type"]) for e in all_edges(files)}


def node_set(files):
    nodes = set()
    for e in all_edges(files):
        nodes.add(e["source_node"])
        nodes.add(e["target_node"])
    return nodes


def type_counts(files):
    return Counter(e["edge_type"] for e in all_edges(files))


# --------------------------------------------------------------------------- shared helpers
def route_for(edge, route_map):
    m = ROUTE_RE.search(edge.get("notes", ""))
    if not m:
        sys.exit(f"ABORT: no route tag in notes for edge "
                 f"{edge['source_node']} -> {edge['target_node']}")
    key = m.group(1)
    if key not in route_map:
        sys.exit(f"ABORT: unknown route {key!r}")
    return route_map[key]


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


# --------------------------------------------------------------------------- batch insert
def apply_batch(modules_dir, route_map, hard_type, batch_path):
    batch = json.loads(Path(batch_path).read_text())
    files = module_files(modules_dir)
    triples = existing_triples(files)

    by_file = {}
    for e in batch:
        dest = route_for(e, route_map)
        if dest in hard_type and e["edge_type"] != hard_type[dest]:
            sys.exit(f"ABORT: edge_type {e['edge_type']!r} routed to {dest} "
                     f"but that module is restricted to {hard_type[dest]!r}")
        key = (e["source_node"], e["target_node"], e["edge_type"])
        if key in triples:
            sys.exit(f"ABORT: duplicate triple already present, refusing insert: {key}")
        triples.add(key)
        by_file.setdefault(dest, []).append(e)

    inserted = []
    for fname, new_edges in by_file.items():
        p = modules_dir / fname
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
    return batch, by_file


def apply_manifest_a(modules_dir, manifest_a_path):
    """Manifest A — edge_modify_fields: attribute-only corrections (verbatim from v12)."""
    manifest = json.loads(Path(manifest_a_path).read_text())
    assert manifest["manifest_type"] == "edge_modify_fields", \
        f"unexpected manifest_type {manifest['manifest_type']!r}"
    target_file = modules_dir / manifest["target_module"]
    edges = json.loads(target_file.read_text())

    # manifest_id is a log label only — it plays no part in matching or application, so a
    # manifest that omits it must not abort the run (T1.2; it did, mid-merge, in V17-B2).
    print(f"\n=== Phase I.2 — Manifest A ({manifest.get('manifest_id', '<unnamed>')}) ===")
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


def apply_manifest_b(modules_dir, route_map, manifest_b_path):
    """Manifest B — edge_semantic_ops: per-op module-scoped semantic edits (verbatim from v12)."""
    manifest = json.loads(Path(manifest_b_path).read_text())
    assert manifest["manifest_type"] == "edge_semantic_ops", \
        f"unexpected manifest_type {manifest['manifest_type']!r}"

    # Log label only — see the note in apply_manifest_a (T1.2).
    print(f"\n=== Phase I.3 — Manifest B ({manifest.get('manifest_id', '<unnamed>')}) ===")
    loaded = {}          # fname -> edges list
    net_delta = 0
    counts = {"delete": 0, "reverse_retarget": 0, "reclassify": 0}

    for op in manifest["operations"]:
        kind = op["op"]
        if kind not in SEMANTIC_DISPATCH:
            sys.exit(f"ABORT: unknown semantic op {kind!r}")
        fname = op["module"]
        if fname not in route_map.values() and not (modules_dir / fname).exists():
            sys.exit(f"ABORT: module {fname!r} not found for op {kind}")
        if fname not in loaded:
            loaded[fname] = json.loads((modules_dir / fname).read_text())
        net_delta += SEMANTIC_DISPATCH[kind](loaded[fname], op)
        counts[kind] += 1

    for fname, edges in loaded.items():
        p = modules_dir / fname
        p.write_text(json.dumps(edges, indent=2))
        json.loads(p.read_text())

    print(f"Manifest B ops: {counts} | net edge delta: {net_delta}")
    return counts


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Unified config-driven Phase I merge.")
    ap.add_argument("--expansion", required=True)
    ap.add_argument("--manifest-a", required=True)
    ap.add_argument("--manifest-b", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--config", default="pipeline_config.json")
    args = ap.parse_args()

    cfg = load_config(args.config)
    modules_dir = cfg["_modules_dir"]
    route_map = cfg["modules"]["route_map"]
    hard_type = cfg["modules"]["edge_type_contract"]

    # T1.3 — manifest pre-flight FIRST: nothing below this line may run against a manifest
    # that cannot be applied. Reads only the manifests and the schema; no module is opened.
    validate_manifests(cfg["_base"], [("Manifest A", args.manifest_a),
                                      ("Manifest B", args.manifest_b)])

    # T1.1 — hash the canonical BEFORE any mutation. phase_i only touches module files, so the
    # canonical still holds the pre-merge state at this point; phase_h fills in the post hash
    # after it regenerates the canonical (see the run-record note below).
    canonical_sha_pre = sha256_file(cfg["_canonical"])

    files = module_files(modules_dir)
    pre_types = type_counts(files)
    pre_nodes = node_set(files)
    pre = {
        "edges": sum(pre_types.values()),
        "nodes": len(pre_nodes),
        "institutional_parent": pre_types.get("institutional_parent", 0),
        "by_edge_type": dict(pre_types),
    }

    batch, by_file = apply_batch(modules_dir, route_map, hard_type, args.expansion)
    n_a = apply_manifest_a(modules_dir, args.manifest_a)
    b_counts = apply_manifest_b(modules_dir, route_map, args.manifest_b)

    # Post-merge counts, recomputed from disk so the delta captures batch + manifest effects.
    files = module_files(modules_dir)
    post_types = type_counts(files)
    post_nodes = node_set(files)
    post_edges = sum(post_types.values())

    all_types = set(pre_types) | set(post_types)
    delta = {
        "edges": post_edges - pre["edges"],
        "nodes": len(post_nodes) - pre["nodes"],
        "institutional_parent": post_types.get("institutional_parent", 0) - pre["institutional_parent"],
        "by_edge_type": {t: post_types.get(t, 0) - pre_types.get(t, 0) for t in all_types},
    }
    new_nodes = sorted(post_nodes - pre_nodes)

    run_record = {
        "version": args.version,
        "config": str(Path(args.config).resolve()),
        # T1.1 — canonical provenance. `_pre` is the canonical as it stood before this merge;
        # `_post` is deliberately left null here and filled by phase_h once it has regenerated
        # the canonical. A committed record with `_pre` populated and `_post` still null is
        # therefore legible evidence of a pipeline that aborted between phase_i and phase_h.
        "canonical_sha256_pre": canonical_sha_pre,
        "canonical_sha256_post": None,
        "inputs": {
            "expansion": str(Path(args.expansion).resolve()),
            "manifest_a": str(Path(args.manifest_a).resolve()),
            "manifest_b": str(Path(args.manifest_b).resolve()),
        },
        "pre": pre,
        "delta": delta,
        "inserted_by_type": dict(Counter(e["edge_type"] for e in batch)),
        "inserted_by_module": {f: len(v) for f, v in by_file.items()},
        "new_nodes": new_nodes,
        "new_node_count": len(new_nodes),
        "manifest_ops": {
            "a_modify_fields": n_a,
            "b_delete": b_counts["delete"],
            "b_reverse_retarget": b_counts["reverse_retarget"],
            "b_reclassify": b_counts["reclassify"],
        },
    }
    record_path = cfg["_base"] / f"merge_run_{args.version}.json"
    record_path.write_text(json.dumps(run_record, indent=2))

    print(f"\nPhase I ({args.version}) complete: +{delta['edges']} net edges "
          f"(batch {len(batch)}), {n_a} field-correction op(s), "
          f"{len(new_nodes)} new node(s).")
    print(f"Run record: {record_path}")


if __name__ == "__main__":
    main()
