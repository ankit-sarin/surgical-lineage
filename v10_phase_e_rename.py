#!/usr/bin/env python3
"""
Phase E — rename 2 Johns Hopkins nodes across all 14 modules + label file.
"""
import json
import glob
import sys
from pathlib import Path

ROOT = Path(__file__).parent

RENAME_MAP = {
    "Johns Hopkins Department of Neurosurgery":
        "Johns Hopkins Hospital Department of Neurosurgery",
    "Johns Hopkins Neurosurgery Residency Program":
        "Johns Hopkins Hospital Neurosurgery Residency Program",
}

def process_modules():
    """Substitute old IDs across id fields and also inside note text so the
    literal-grep validation passes. Track id-field and note-text counts separately."""
    totals = {}
    for fpath in sorted(ROOT.glob("[0-9][0-9]_*.json")):
        fname = fpath.name
        if fname.startswith("00_") or fname.startswith("99_"):
            continue
        edges = json.loads(fpath.read_text())
        id_count = 0
        note_count = 0
        for e in edges:
            if e["source_node"] in RENAME_MAP:
                e["source_node"] = RENAME_MAP[e["source_node"]]
                id_count += 1
            if e["target_node"] in RENAME_MAP:
                e["target_node"] = RENAME_MAP[e["target_node"]]
                id_count += 1
            notes = e.get("notes", "")
            if notes:
                new_notes = notes
                for old, new in RENAME_MAP.items():
                    if old in new_notes:
                        new_notes = new_notes.replace(old, new)
                        note_count += 1
                if new_notes != notes:
                    e["notes"] = new_notes
        if id_count + note_count > 0:
            fpath.write_text(json.dumps(edges, indent=2))
        totals[fname] = {"id": id_count, "note": note_count}
    return totals


def process_labels():
    p = ROOT / "node_labels_adjudicated.json"
    labels = json.loads(p.read_text())
    updated = 0
    for entry in labels:
        if entry.get("id") in RENAME_MAP:
            entry["id"] = RENAME_MAP[entry["id"]]
            updated += 1
    if updated:
        p.write_text(json.dumps(labels, indent=2))
    return updated


def verify_zero_old_refs():
    """Grep every module file and label file for any lingering old ID."""
    problems = []
    for fpath in sorted(ROOT.glob("[0-9][0-9]_*.json")):
        if fpath.name.startswith("00_") or fpath.name.startswith("99_"):
            continue
        txt = fpath.read_text()
        for old in RENAME_MAP:
            if old in txt:
                problems.append((fpath.name, old))
    lbl = (ROOT / "node_labels_adjudicated.json").read_text()
    for old in RENAME_MAP:
        if old in lbl:
            problems.append(("node_labels_adjudicated.json", old))
    return problems


def main():
    module_totals = process_modules()
    label_updated = process_labels()
    problems = verify_zero_old_refs()

    print("=== Phase E — Johns Hopkins rename ===\n")
    print("Per-module modifications (id | note-text):")
    grand_id = 0
    grand_note = 0
    for n, c in module_totals.items():
        if c["id"] + c["note"] > 0:
            print(f"  {n}: id={c['id']}  note-text={c['note']}")
            grand_id += c["id"]
            grand_note += c["note"]
    print(f"\nTotal id-field substitutions: {grand_id}")
    print(f"Total note-text substitutions: {grand_note}")
    print(f"Label file entries updated: {label_updated}")

    print(f"\nLingering old-ID references: {len(problems)}")
    for fn, old in problems:
        print(f"  {fn}: still contains {old!r}")
    if problems:
        sys.exit(1)

    # Edge count invariant
    total_edges = 0
    for fpath in sorted(ROOT.glob("[0-9][0-9]_*.json")):
        if fpath.name.startswith("00_") or fpath.name.startswith("99_"):
            continue
        total_edges += len(json.loads(fpath.read_text()))
    print(f"\nEdge count after rename: {total_edges}")
    assert total_edges == 452, f"Edge count drift: {total_edges} != 452"
    print("Phase E validation: PASS")


if __name__ == "__main__":
    main()
