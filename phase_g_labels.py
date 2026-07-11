#!/usr/bin/env python3
"""
Unified Phase G — reconcile the node-labels file to the post-merge canonical node set.

Historically this step could only APPEND stub entries for new nodes; it had no path to
drop labels for nodes that no longer exist, so any delete batch left label_count >
node_count and the terminal parity assert failed — forcing a manual label-file edit
(the V15-B2 workaround). This version reconciles labels to the ground-truth node set in
a single pass — additions AND removals — reporting every change by name:

  - APPEND a stub for every canonical node lacking a label (existing behavior, preserved).
  - PRUNE every label whose node is no longer in the canonical node set (new behavior).

Ground truth is the SAME regenerated canonical node set phase_g has always validated
against (derived from the numbered module files) — no second source of truth is introduced.
Existing (retained) label entries are never modified: an integrity check verifies each
retained entry is byte-identical to before. A mass-prune safety rail (--max-prune) aborts
loudly with the full itemized list if the prune count is unexpectedly large (e.g. a typo'd
rename that orphaned many nodes), rather than silently executing it. Append is not capped.

The terminal parity assert (label_count == node_count) is preserved — reconciliation makes
it pass honestly; it is not weakened or removed. Paths come from --config.
"""
import argparse
import json
import hashlib
import sys
from pathlib import Path
from collections import defaultdict


STUB_LABEL_SHORT_SOURCE = "stub_pending_adjudication"


class MassPruneError(Exception):
    """Raised when the number of labels to prune exceeds the configured --max-prune rail.

    Carries the itemized list of label entries that WOULD be pruned so the caller can
    surface exactly what tripped the guard. No mutation is performed when this is raised.
    """

    def __init__(self, to_prune, max_prune):
        self.to_prune = to_prune
        self.max_prune = max_prune
        super().__init__(
            f"prune count {len(to_prune)} exceeds --max-prune {max_prune}"
        )


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


def make_stub(nid, ntype, degree):
    """Build a fresh stub label entry (schema preserved verbatim from the append-only era)."""
    return {
        "id": nid,
        "type": ntype,
        "degree": degree,
        "label_short": "",
        "label_short_source": STUB_LABEL_SHORT_SOURCE,
        "reviewed": False,
    }


def reconcile_labels(labels, canonical, max_prune=10):
    """Reconcile a label list to the canonical node set in one pass — pure, no I/O.

    Args:
        labels:    list of label dicts (each with at least an "id" key).
        canonical: dict node_id -> (type, degree), the authoritative node set.
        max_prune: safety rail; if more than this many labels would be pruned, raise
                   MassPruneError WITHOUT producing a reconciled list.

    Returns:
        (reconciled, appended, pruned) where
          reconciled: new label list == canonical node set (retained originals, in original
                      order, followed by new stubs sorted by id),
          appended:   sorted list of node ids that received a new stub,
          pruned:     list of the original label entries removed (node no longer canonical).

    Raises:
        MassPruneError: if len(pruned) > max_prune (nothing is mutated).
    """
    existing_ids = {e["id"] for e in labels}
    canon_ids = set(canonical)

    missing = sorted(canon_ids - existing_ids)
    prune_ids = existing_ids - canon_ids
    pruned = [e for e in labels if e["id"] in prune_ids]

    if len(pruned) > max_prune:
        raise MassPruneError(pruned, max_prune)

    retained = [e for e in labels if e["id"] in canon_ids]
    new_stubs = [make_stub(nid, canonical[nid][0], canonical[nid][1]) for nid in missing]
    reconciled = retained + new_stubs
    return reconciled, missing, pruned


def _print_itemized(header, rows):
    """rows: list of (id, type) tuples. Loud, one line per item, never silent."""
    print(header)
    if not rows:
        print("  (none)")
        return
    for nid, ntype in rows:
        print(f"  - [{ntype}] {nid}")


def main():
    ap = argparse.ArgumentParser(description="Unified config-driven Phase G label reconcile.")
    ap.add_argument("--config", default="pipeline_config.json")
    ap.add_argument("--version", required=False, default=None)
    ap.add_argument("--max-prune", type=int, default=10,
                    help="Abort (do not write) if more than this many labels would be pruned.")
    args = ap.parse_args()

    cfg = load_config(args.config)
    label_path = cfg["_node_labels"]

    labels = json.loads(label_path.read_text())
    pre_count = len(labels)
    # Per-id snapshot so we can prove every RETAINED entry is byte-identical afterward
    # (allows removal, still forbids silent modification of a surviving entry).
    original_by_id = {e["id"]: json.dumps(e, sort_keys=True) for e in labels}

    edges = load_all_edges(cfg["_modules_dir"])
    canonical = compute_canonical(edges)

    print(f"Canonical node count: {len(canonical)}")
    print(f"Pre-task label entries: {pre_count}")

    try:
        reconciled, appended, pruned = reconcile_labels(labels, canonical, args.max_prune)
    except MassPruneError as exc:
        print(f"\nABORT: prune count {len(exc.to_prune)} exceeds --max-prune {exc.max_prune}.")
        print("The following labels WOULD have been pruned (label file left unmodified):")
        _print_itemized(f"Pruned candidates ({len(exc.to_prune)}):",
                        [(e["id"], e.get("type", "?")) for e in exc.to_prune])
        print("\nPhase G validation: ABORTED (mass-prune guard tripped)")
        sys.exit(2)

    # --- loud, itemized report of exactly what changed, BEFORE the parity assert ---
    _print_itemized(f"\nAppended stubs ({len(appended)}):",
                    [(nid, canonical[nid][0]) for nid in appended])
    _print_itemized(f"\nPruned labels ({len(pruned)}):",
                    [(e["id"], e.get("type", "?")) for e in pruned])

    # --- integrity: no retained existing entry may have been modified ---
    for e in reconciled:
        snap = original_by_id.get(e["id"])
        if snap is not None and json.dumps(e, sort_keys=True) != snap:
            print(f"\nFAIL: existing label entry was modified: {e['id']!r}")
            sys.exit(1)

    label_path.write_text(json.dumps(reconciled, indent=2))
    post_count = len(reconciled)

    print(f"\nPost-task label entries: {post_count}")
    print(f"Entries appended: {len(appended)} | entries pruned: {len(pruned)}")

    append_types = defaultdict(int)
    for nid in appended:
        append_types[canonical[nid][0]] += 1
    prune_types = defaultdict(int)
    for e in pruned:
        prune_types[e.get("type", "?")] += 1
    print(f"Appended by type: {dict(append_types)} | pruned by type: {dict(prune_types)}")

    # Terminal parity assert — reconciliation makes this pass honestly.
    assert post_count == len(canonical), f"mismatch: {post_count} != {len(canonical)}"
    print("\nPhase G validation: PASS")


if __name__ == "__main__":
    main()
