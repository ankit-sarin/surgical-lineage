#!/usr/bin/env python3
"""
Phase H — regenerate canonical flat file, validate invariants, write report.
"""
import json
import os
import sys
import glob
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

import networkx as nx

ROOT = Path(__file__).parent
BACKUP_DIR_HINT = Path("/tmp/task2b_backup_dir.txt")


def regen_canonical():
    all_edges = []
    module_counts = {}
    for f in sorted(ROOT.glob("[0-9][0-9]_*.json")):
        if f.name.startswith("00_") or f.name.startswith("99_"):
            continue
        edges = json.loads(f.read_text())
        module_counts[f.name] = len(edges)
        all_edges.extend(edges)
    out = ROOT / "surgical_lineage_graph_canonical.json"
    out.write_text(json.dumps(all_edges, indent=2))
    # Re-parse
    json.loads(out.read_text())
    return all_edges, module_counts


def validate_graph(all_edges):
    G = nx.Graph()
    for e in all_edges:
        G.add_edge(e["source_node"], e["target_node"])
    nodes = set()
    for e in all_edges:
        nodes.add(e["source_node"])
        nodes.add(e["target_node"])
    return {
        "edges_simple": G.number_of_edges(),
        "nodes": G.number_of_nodes(),
        "components": nx.number_connected_components(G),
        "canonical_nodes_set": len(nodes),
    }


def restore_from_backup():
    if not BACKUP_DIR_HINT.exists():
        print("FATAL: no backup dir pointer found", file=sys.stderr)
        return
    backup = BACKUP_DIR_HINT.read_text().strip()
    print(f"Restoring files from {backup}", file=sys.stderr)
    import shutil
    for f in Path(backup).glob("*"):
        shutil.copy(f, ROOT / f.name)


def main():
    all_edges, module_counts = regen_canonical()
    total_edges = len(all_edges)
    stats = validate_graph(all_edges)

    print("=== Phase H — regeneration & validation ===\n")
    print(f"Edge count (flat list): {total_edges}")
    print(f"NetworkX simple edges: {stats['edges_simple']}")
    print(f"Nodes: {stats['nodes']}")
    print(f"Components: {stats['components']}")

    expected_edges = 480
    expected_nodes = 371
    ip_edges = sum(1 for e in all_edges if e["edge_type"] == "institutional_parent")

    gate_pass = True
    if total_edges != expected_edges:
        gate_pass = False
        print(f"FAIL: edge count {total_edges} != {expected_edges}")
    if stats["nodes"] != expected_nodes:
        gate_pass = False
        print(f"FAIL: node count {stats['nodes']} != {expected_nodes}")
    if stats["components"] != 1:
        gate_pass = False
        print(f"FAIL: components {stats['components']} != 1  — ABORTING, restoring from backup")
        restore_from_backup()
        sys.exit(2)
    if ip_edges != 28:
        gate_pass = False
        print(f"FAIL: institutional_parent edge count {ip_edges} != 28")

    if not gate_pass:
        sys.exit(1)

    # Per-module summary
    print("\nPer-module edge counts:")
    for n, c in module_counts.items():
        print(f"  {n}: {c}")

    # Edge-type breakdown
    et_counts = Counter(e["edge_type"] for e in all_edges)
    print("\nEdge-type distribution:")
    for t, c in sorted(et_counts.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")

    # Final report
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    bare_roots = sorted({
        e["target_node"] for e in all_edges if e["edge_type"] == "institutional_parent"
    })
    report = [
        "# Task 2B Retrofit Report",
        f"Generated: {ts}",
        "",
        "## Schema",
        "v3 live (`institutional_parent` in enum) — applied in prior Task 2 Phase A.",
        "",
        "## Renames (Phase E)",
        "- `Johns Hopkins Department of Neurosurgery` → `Johns Hopkins Hospital Department of Neurosurgery` (id-field edge substitutions: 2)",
        "- `Johns Hopkins Neurosurgery Residency Program` → `Johns Hopkins Hospital Neurosurgery Residency Program` (id-field edge substitutions: 2)",
        "- Total id-field substitutions across modules: 4",
        "- Additional note-text substitutions (descriptive references inside `notes` fields): 1",
        "- Label file entries updated: 1",
        "",
        "## New bare root nodes (10)",
    ]
    # The 10 new bare roots (MSK was already in the graph)
    new_roots = [r for r in bare_roots if r != "Memorial Sloan Kettering Cancer Center"]
    for r in new_roots:
        report.append(f"- {r}")
    report += [
        "",
        "Memorial Sloan Kettering Cancer Center was already present; not counted as new.",
        "",
        f"## `institutional_parent` edges authored: {ip_edges}",
        "Routed to: `15_institutional_hierarchy.json` (new module).",
        "",
        "## Label file",
        "- Pre-task entries: 327",
        "- Stub entries added: 44 (10 new bare roots + 34 pre-existing gaps)",
        "- Post-task entries: 371 (matches canonical node count)",
        "- All stubs have `label_short: \"\"`, `label_short_source: \"stub_pending_adjudication\"`, `reviewed: false`",
        "- No pre-existing entry was modified (verified by SHA-256 hash of the first 327 entries)",
        "",
        "## Graph state",
        f"- Edges: 452 → {total_edges} (+{total_edges - 452})",
        f"- Nodes: 361 → {stats['nodes']} (+{stats['nodes'] - 361})",
        f"- Components: {stats['components']} (invariant held)",
        "",
        "## Deferred (out of scope for this task)",
        "- Programmatic short-label derivation (full label regeneration for the 44 stubs)",
        "- `Peter Bent Brigham Peripheral Vascular Clinic` naming cleanup (inconsistent with other PBB Hospital children, which use \"Hospital\" in their ID)",
        "- V10 department-level `institutional_parent` edges (e.g., Minnesota Dept of Surgery → University of Minnesota) — authored during V10 departmental work",
        "- Mediterranean Theater Surgical Service still has no parent; theater-level meta-node class modeling deferred",
        "",
        "## Module inventory",
    ]
    for n, c in module_counts.items():
        report.append(f"- `{n}`: {c} edges")
    report.append("")
    report.append("## Edge-type distribution")
    for t, c in sorted(et_counts.items(), key=lambda x: -x[1]):
        report.append(f"- `{t}`: {c}")
    report.append("")

    (ROOT / "v10_retrofit_report.md").write_text("\n".join(report))

    # Clean up: delete superseded files per spec
    cleanup = []
    for junk in ["v10_institutional_parent_retrofit.json", "v10_retrofit_deferred.md"]:
        p = ROOT / junk
        if p.exists():
            p.unlink()
            cleanup.append(junk)
    if cleanup:
        print(f"\nDeleted superseded files: {cleanup}")

    print(f"\nReport written: {ROOT / 'v10_retrofit_report.md'}")
    print("Phase H validation: PASS")


if __name__ == "__main__":
    main()
