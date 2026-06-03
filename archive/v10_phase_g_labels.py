#!/usr/bin/env python3
"""
Phase G — append stub entries to node_labels_adjudicated.json for every node
in the post-retrofit canonical graph that lacks an entry. No existing entry
is modified.
"""
import json
import hashlib
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent
LABEL_PATH = ROOT / "node_labels_adjudicated.json"


def load_all_edges():
    edges = []
    for f in sorted(ROOT.glob("[0-9][0-9]_*.json")):
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
    labels = json.loads(LABEL_PATH.read_text())
    pre_count = len(labels)

    # Snapshot of pre-existing entries for unchanged-verification
    pre_snapshot = json.dumps(labels, sort_keys=True)
    pre_hash = hashlib.sha256(pre_snapshot.encode()).hexdigest()

    existing_ids = {entry["id"] for entry in labels}

    edges = load_all_edges()
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

    LABEL_PATH.write_text(json.dumps(labels, indent=2))
    post_count = len(labels)

    print(f"\nPost-task label entries: {post_count}")
    print(f"Entries added: {post_count - pre_count}")
    assert post_count == len(canonical), f"mismatch: {post_count} != {len(canonical)}"

    # Print a sample of stubs added (type breakdown)
    type_counts = defaultdict(int)
    for nid in missing:
        type_counts[canonical[nid][0]] += 1
    print(f"Stubs added by type: {dict(type_counts)}")

    # Show new bare roots specifically
    bare_roots = [
        "Washington University", "Mayo Clinic", "Massachusetts General Hospital",
        "Peter Bent Brigham Hospital", "Johns Hopkins Hospital", "Cleveland Clinic",
        "University of Miami", "University of Minnesota",
        "University of Pennsylvania", "University of Pittsburgh",
        "Memorial Sloan Kettering Cancer Center",
    ]
    print("\nBare-root stub status:")
    for r in bare_roots:
        if r in missing:
            print(f"  NEW STUB: {r}")
        elif r in existing_ids:
            print(f"  pre-existing entry: {r}")
        else:
            print(f"  WARNING: {r} not in canonical node set")

    print("\nPhase G validation: PASS")


if __name__ == "__main__":
    main()
