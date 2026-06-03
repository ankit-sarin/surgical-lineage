#!/usr/bin/env python3
"""
Unified Phase G — append stub entries to the node-labels file for every node in the
post-merge canonical graph that lacks an entry. No existing entry is modified.

Logic preserved verbatim from v10_phase_g_labels.py (stub schema, SHA-256 unchanged-guard
over pre-existing entries, node-parity assertion). Paths come from --config.
"""
import argparse
import json
import hashlib
import sys
from pathlib import Path
from collections import defaultdict


def load_config(config_path):
    cfg = json.loads(Path(config_path).read_text())
    base = Path(config_path).resolve().parent
    cfg["_base"] = base
    cfg["_modules_dir"] = (base / cfg["paths"]["modules_dir"]).resolve()
    cfg["_node_labels"] = (base / cfg["paths"]["node_labels"]).resolve()
    return cfg


def load_all_edges(modules_dir):
    edges = []
    for f in sorted(modules_dir.glob("[0-9][0-9]_*.json")):
        if f.name.startswith("00_") or f.name.startswith("99_"):
            continue
        edges.extend(json.loads(f.read_text()))
    return edges


def compute_canonical(edges):
    """Return dict (id) -> (type, degree)."""
    info = {}
    degree = defaultdict(int)
    for e in edges:
        s, st = e["source_node"], e["source_node_type"]
        t, tt = e["target_node"], e["target_node_type"]
        info[s] = st
        info[t] = tt
        degree[s] += 1
        degree[t] += 1
    return {n: (info[n], degree[n]) for n in info}


def main():
    ap = argparse.ArgumentParser(description="Unified config-driven Phase G label stubs.")
    ap.add_argument("--config", default="pipeline_config.json")
    ap.add_argument("--version", required=False, default=None)
    args = ap.parse_args()

    cfg = load_config(args.config)
    label_path = cfg["_node_labels"]

    labels = json.loads(label_path.read_text())
    pre_count = len(labels)

    # Snapshot of pre-existing entries for unchanged-verification
    pre_snapshot = json.dumps(labels, sort_keys=True)
    pre_hash = hashlib.sha256(pre_snapshot.encode()).hexdigest()

    existing_ids = {entry["id"] for entry in labels}

    edges = load_all_edges(cfg["_modules_dir"])
    canonical = compute_canonical(edges)
    missing = sorted(set(canonical) - existing_ids)

    print(f"Canonical node count: {len(canonical)}")
    print(f"Pre-task label entries: {pre_count}")
    print(f"Missing nodes: {len(missing)}")

    # Append stubs
    for nid in missing:
        ntype, deg = canonical[nid]
        labels.append({
            "id": nid,
            "type": ntype,
            "degree": deg,
            "label_short": "",
            "label_short_source": "stub_pending_adjudication",
            "reviewed": False,
        })

    # Verify first pre_count entries hash identical
    post_snapshot = json.dumps(labels[:pre_count], sort_keys=True)
    post_hash = hashlib.sha256(post_snapshot.encode()).hexdigest()
    if pre_hash != post_hash:
        print("FAIL: pre-existing entries were modified")
        sys.exit(1)

    label_path.write_text(json.dumps(labels, indent=2))
    post_count = len(labels)

    print(f"\nPost-task label entries: {post_count}")
    print(f"Entries added: {post_count - pre_count}")
    assert post_count == len(canonical), f"mismatch: {post_count} != {len(canonical)}"

    # Type breakdown of stubs added
    type_counts = defaultdict(int)
    for nid in missing:
        type_counts[canonical[nid][0]] += 1
    print(f"Stubs added by type: {dict(type_counts)}")
    print("\nPhase G validation: PASS")


if __name__ == "__main__":
    main()
