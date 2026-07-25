#!/usr/bin/env python3
"""
Unified Phase H — regenerate the canonical flat file and gate on a DERIVED expected state.

Canonical regeneration is byte-for-byte identical to v10_phase_h_apply.py (same sorted glob
of numbered modules excluding 00_/99_, same json.dumps(indent=2) serialization).

The hardcoded per-version baseline gate is REPLACED by a derived gate:
  expected_post = run_record.pre + run_record.delta
and the regenerated canonical must match expected_post on total edges, total nodes,
per-edge-type counts, and institutional_parent count — PLUS every structural invariant
declared true in the config (zero_duplicate_triples, zero_node_type_conflicts,
label_node_parity). Connectivity (single_component) was DEMOTED to a reported metric in
V17-INVARIANT — see component_report(); it prints an island report + threshold warning but
never changes the exit code.

There are NO hardcoded version constants in this file. The legacy v10_retrofit_report.md
emission is retired (its still-useful figures are folded into the diagnostic audit report).
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx


def load_config(config_path):
    cfg = json.loads(Path(config_path).read_text())
    base = Path(config_path).resolve().parent
    cfg["_base"] = base
    cfg["_modules_dir"] = (base / cfg["paths"]["modules_dir"]).resolve()
    cfg["_canonical"] = (base / cfg["paths"]["canonical"]).resolve()
    cfg["_node_labels"] = (base / cfg["paths"]["node_labels"]).resolve()
    cfg["_schema"] = (base / cfg["paths"].get("schema", "00_schema.json")).resolve()
    return cfg


def regen_canonical(modules_dir, canonical_path):
    all_edges = []
    module_counts = {}
    for f in sorted(modules_dir.glob("[0-9][0-9]_*.json")):
        if f.name.startswith("00_") or f.name.startswith("99_"):
            continue
        edges = json.loads(f.read_text())
        module_counts[f.name] = len(edges)
        all_edges.extend(edges)
    canonical_path.write_text(json.dumps(all_edges, indent=2))
    json.loads(canonical_path.read_text())  # re-parse guard
    return all_edges, module_counts


def graph_stats(all_edges):
    G = nx.Graph()
    nodes = set()
    for e in all_edges:
        G.add_edge(e["source_node"], e["target_node"])
        nodes.add(e["source_node"])
        nodes.add(e["target_node"])
    return {
        "edges": len(all_edges),
        "nodes": len(nodes),
        "node_set": nodes,
        "components": nx.number_connected_components(G),
        "by_edge_type": dict(Counter(e["edge_type"] for e in all_edges)),
        "institutional_parent": sum(1 for e in all_edges if e["edge_type"] == "institutional_parent"),
    }


def duplicate_triples(all_edges):
    seen = Counter((e["source_node"], e["target_node"], e["edge_type"]) for e in all_edges)
    return [k for k, c in seen.items() if c > 1]


def node_type_conflicts(all_edges):
    types = defaultdict(set)
    for e in all_edges:
        types[e["source_node"]].add(e["source_node_type"])
        types[e["target_node"]].add(e["target_node_type"])
    return {n: sorted(ts) for n, ts in types.items() if len(ts) > 1}


def component_report(all_edges, comp_cfg):
    """REPORTED connectivity metric (demoted from a blocking invariant in V17-INVARIANT).

    Returns (lines, warn). Builds the undirected graph, enumerates connected components, and
    ALWAYS lists the full member set of every non-giant component (island) so fragmentation is
    visible in merge output rather than fatal. `warn` is True when the observed component count
    exceeds comp_cfg['expected_components'] or the largest island exceeds
    comp_cfg['max_island_size']. Neither the report nor `warn` ever affects the exit code —
    connectivity is a measured property of the current graph, not a per-version invariant.
    """
    G = nx.Graph()
    for e in all_edges:
        G.add_edge(e["source_node"], e["target_node"])
    comps = sorted((sorted(c) for c in nx.connected_components(G)), key=len, reverse=True)
    sizes = [len(c) for c in comps]
    islands = comps[1:]  # every component other than the largest (giant)
    largest_island = max((len(i) for i in islands), default=0)
    expected = comp_cfg.get("expected_components", 1)
    max_island = comp_cfg.get("max_island_size", 0)
    warn = (len(comps) > expected) or (largest_island > max_island)

    lines = ["=== Phase H — connectivity report (REPORTED METRIC; does not affect exit code) ==="]
    lines.append(f"connected components: {len(comps)} (expected {expected}); component sizes: "
                 f"{sizes}; largest island: {largest_island} node(s) (max tolerated {max_island})")
    if islands:
        lines.append(f"islands — every non-giant component ({len(islands)}), members listed:")
        for i, isl in enumerate(islands, 1):
            lines.append(f"  island {i} ({len(isl)} node(s)): {isl}")
    else:
        lines.append(f"islands: none — single giant component of {sizes[0] if sizes else 0} node(s).")
    if warn:
        reasons = []
        if len(comps) > expected:
            reasons.append(f"components {len(comps)} > expected {expected}")
        if largest_island > max_island:
            reasons.append(f"largest island {largest_island} > max tolerated {max_island}")
        lines.append(f"  *** WARNING: connectivity exceeds configured threshold "
                     f"({'; '.join(reasons)}) — possible NEW fragmentation; REPORTED, not "
                     f"blocking — review required. ***")
    return lines, warn


def schema_validate_warn(all_edges, schema_path):
    """WARN-ONLY validation of the regenerated canonical against 00_schema.json.

    Emits a clearly-labelled warning block naming every violating edge (index +
    source/target/edge_type + the failing constraint). This function NEVER raises and NEVER
    affects the caller's exit code — it is deliberately warn-only for one merge cycle so latent
    typing defects surface without halting a batch mid-run. If jsonschema is unavailable, it
    emits a single warning and returns rather than hard-failing.
    """
    print("\n=== Phase H — schema validation (WARN-ONLY; does not affect exit code) ===")
    try:
        import jsonschema
    except ImportError:
        print("  WARN: jsonschema not installed — schema validation skipped "
              "(pip install -r requirements.txt to enable). Exit code unaffected.")
        return
    if not schema_path.exists():
        print(f"  WARN: schema not found at {schema_path} — validation skipped. "
              f"Exit code unaffected.")
        return
    schema = json.loads(schema_path.read_text())
    validator = jsonschema.Draft7Validator(schema["items"])
    violations = 0
    for i, e in enumerate(all_edges):
        for err in sorted(validator.iter_errors(e), key=lambda x: list(x.path)):
            violations += 1
            loc = ".".join(str(p) for p in err.path) or "(edge root)"
            print(f"  WARN edge[{i}] {e.get('source_node', '?')} -> {e.get('target_node', '?')} "
                  f"[{e.get('edge_type', '?')}]: {loc}: {err.message}")
    if violations == 0:
        print(f"  OK: all {len(all_edges)} edges validate against {schema_path.name}.")
    else:
        print(f"  {violations} schema violation(s) across {len(all_edges)} edges "
              f"(WARN-ONLY — merge not blocked).")


def main():
    ap = argparse.ArgumentParser(description="Unified config-driven Phase H apply + derived gate.")
    ap.add_argument("--version", required=True)
    ap.add_argument("--config", default="pipeline_config.json")
    ap.add_argument("--run-record", required=True)
    args = ap.parse_args()

    cfg = load_config(args.config)
    inv = cfg["invariants"]
    rec = json.loads(Path(args.run_record).read_text())
    pre, delta = rec["pre"], rec["delta"]

    all_edges, module_counts = regen_canonical(cfg["_modules_dir"], cfg["_canonical"])
    stats = graph_stats(all_edges)

    # Derived expectations: expected_post = pre + delta (NO hardcoded baseline).
    exp_edges = pre["edges"] + delta["edges"]
    exp_nodes = pre["nodes"] + delta["nodes"]
    exp_ip = pre["institutional_parent"] + delta["institutional_parent"]
    all_types = set(pre["by_edge_type"]) | set(delta["by_edge_type"])
    exp_types = {t: pre["by_edge_type"].get(t, 0) + delta["by_edge_type"].get(t, 0)
                 for t in all_types}
    exp_types = {t: c for t, c in exp_types.items() if c != 0}

    print("=== Phase H — regeneration & DERIVED gate ===\n")
    print(f"Run record: {Path(args.run_record).resolve()}  (version {rec.get('version')})")
    print(f"pre {pre['edges']}e/{pre['nodes']}n/ip{pre['institutional_parent']}  "
          f"delta {delta['edges']:+d}e/{delta['nodes']:+d}n/ip{delta['institutional_parent']:+d}  "
          f"=> expected_post {exp_edges}e/{exp_nodes}n/ip{exp_ip}")
    print(f"Regenerated canonical: {stats['edges']}e / {stats['nodes']}n / "
          f"{stats['components']} component(s) / ip {stats['institutional_parent']}\n")

    failures = []

    # --- derived count gate ---
    if stats["edges"] != exp_edges:
        failures.append(f"edge count {stats['edges']} != expected_post {exp_edges}")
    if stats["nodes"] != exp_nodes:
        failures.append(f"node count {stats['nodes']} != expected_post {exp_nodes}")
    if stats["institutional_parent"] != exp_ip:
        failures.append(f"institutional_parent {stats['institutional_parent']} != expected_post {exp_ip}")
    if stats["by_edge_type"] != exp_types:
        # show the precise per-type divergence
        keys = set(stats["by_edge_type"]) | set(exp_types)
        diffs = {k: (exp_types.get(k, 0), stats["by_edge_type"].get(k, 0))
                 for k in keys if exp_types.get(k, 0) != stats["by_edge_type"].get(k, 0)}
        failures.append(f"per-edge-type mismatch (expected, actual): {diffs}")

    # --- structural invariants (config-declared) ---
    # NOTE: single_component was DEMOTED to a reported metric in V17-INVARIANT (see
    # component_report() below) — it no longer contributes to `failures`. The invariants that
    # remain BLOCKING are duplicate triples, node-type conflicts, and label/node parity.
    if inv.get("zero_duplicate_triples"):
        dups = duplicate_triples(all_edges)
        if dups:
            failures.append(f"zero_duplicate_triples violated: {len(dups)} dup triple(s) e.g. {dups[:3]}")
    if inv.get("zero_node_type_conflicts"):
        conflicts = node_type_conflicts(all_edges)
        if conflicts:
            sample = dict(list(conflicts.items())[:3])
            failures.append(f"zero_node_type_conflicts violated: {len(conflicts)} node(s) e.g. {sample}")
    if inv.get("label_node_parity"):
        labels = json.loads(cfg["_node_labels"].read_text())
        label_ids = {e["id"] for e in labels}
        canon_nodes = stats["node_set"]
        if label_ids != canon_nodes:
            only_lbl = sorted(label_ids - canon_nodes)[:3]
            only_can = sorted(canon_nodes - label_ids)[:3]
            failures.append(
                f"label_node_parity violated: labels={len(label_ids)} canonical={len(canon_nodes)} "
                f"(labels-only e.g. {only_lbl}; canonical-only e.g. {only_can})")

    print("Per-module edge counts:")
    for n, c in module_counts.items():
        print(f"  {n}: {c}")
    print("\nEdge-type distribution:")
    for t, c in sorted(stats["by_edge_type"].items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")

    # Warn-only schema validation — informational; deliberately does NOT touch `failures`.
    schema_validate_warn(all_edges, cfg["_schema"])

    # Reported connectivity metric — informational; deliberately does NOT touch `failures`.
    comp_lines, _comp_warn = component_report(all_edges, cfg.get("component_report", {}))
    print()
    for line in comp_lines:
        print(line)

    if failures:
        print("\nPhase H DERIVED GATE: FAIL")
        for f in failures:
            print(f"  FAIL: {f}")
        sys.exit(1)

    print("\nPhase H DERIVED GATE: PASS "
          f"(counts match pre+delta; invariants {', '.join(k for k, v in inv.items() if v)} all hold)")


if __name__ == "__main__":
    main()
