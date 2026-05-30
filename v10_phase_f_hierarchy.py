#!/usr/bin/env python3
"""
Phase F — author 15_institutional_hierarchy.json with 28 institutional_parent edges.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent

PARENT_CHILDREN = [
    ("Washington University", [
        "Washington University Chest Service",
        "Washington University Department of Neurosurgery",
        "Washington University Division of Plastic Surgery",
        "Washington University Division of Urologic Surgery",
    ]),
    ("Mayo Clinic", [
        "Mayo Clinic Department of Surgery",
        "Mayo Clinic Department of Orthopedic Surgery",
        "Mayo Clinic Section of Proctology",
    ]),
    ("Massachusetts General Hospital", [
        "Massachusetts General Hospital Department of Surgery",
        "Massachusetts General Hospital End Result System",
        "Massachusetts General Hospital Thoracic Surgical Service",
    ]),
    ("Peter Bent Brigham Hospital", [
        "Peter Bent Brigham Hospital Department of Surgery",
        "Peter Bent Brigham Hospital Neurosurgical Program",
        "Peter Bent Brigham Hospital Renal Transplant Program",
        "Peter Bent Brigham Peripheral Vascular Clinic",
    ]),
    ("Johns Hopkins Hospital", [
        "Johns Hopkins Hospital Department of Surgery",
        "Johns Hopkins Hospital Department of Neurosurgery",
        "Johns Hopkins Hospital Neurosurgery Residency Program",
    ]),
    ("Cleveland Clinic", [
        "Cleveland Clinic Department of Colorectal Surgery",
        "Cleveland Clinic Department of General Surgery",
    ]),
    ("University of Miami", [
        "University of Miami Division of Plastic Surgery",
        "University of Miami Transplant Program",
    ]),
    ("University of Minnesota", [
        "University of Minnesota Open Heart Surgery Program",
        "University of Minnesota Transplant Program",
    ]),
    ("University of Pennsylvania", [
        "University of Pennsylvania Department of Surgery",
        "University of Pennsylvania Department of Neurosurgery",
    ]),
    ("University of Pittsburgh", [
        "University of Pittsburgh Department of Surgery",
        "University of Pittsburgh Transplant Program",
    ]),
    ("Memorial Sloan Kettering Cancer Center", [
        "Memorial Sloan Kettering HPB Service",
    ]),
]


def load_all_modules():
    edges = []
    for f in sorted(ROOT.glob("[0-9][0-9]_*.json")):
        if f.name.startswith("00_") or f.name.startswith("99_"):
            continue
        edges.extend(json.loads(f.read_text()))
    return edges


def collect_inst_nodes(edges):
    nodes = set()
    for e in edges:
        if e["source_node_type"] == "institution":
            nodes.add(e["source_node"])
        if e["target_node_type"] == "institution":
            nodes.add(e["target_node"])
    return nodes


def find_source_edge_for_child(child, all_edges):
    """Return (earliest_start_year, evidence_citation, evidence_type, evidence_locator, source_edge_desc).

    Priority:
      1. institutional_founder edge with target_node == child (earliest start_year)
      2. governance_leadership edge with target_node == child (earliest start_year)
      3. ANY edge involving child (earliest start_year) — fallback
    """
    founders = [e for e in all_edges
                if e["edge_type"] == "institutional_founder" and e["target_node"] == child]
    govs = [e for e in all_edges
            if e["edge_type"] == "governance_leadership" and e["target_node"] == child]
    any_edge = [e for e in all_edges
                if e["source_node"] == child or e["target_node"] == child]

    picked, source_desc = None, None
    if founders:
        picked = min(founders, key=lambda e: e.get("start_year") or 99999)
        source_desc = "institutional_founder edge"
    elif govs:
        picked = min(govs, key=lambda e: e.get("start_year") or 99999)
        source_desc = "earliest governance_leadership edge"
    elif any_edge:
        picked = min(any_edge, key=lambda e: e.get("start_year") or 99999)
        source_desc = f"earliest edge ({picked['edge_type']})"
    else:
        return None

    return {
        "start_year": picked.get("start_year"),
        "evidence_citation": picked.get("evidence_citation", ""),
        "evidence_type": picked.get("evidence_type", "institutional_archive"),
        "evidence_locator": picked.get("evidence_locator", ""),
        "source_desc": source_desc,
    }


def main():
    all_edges = load_all_modules()
    inst_nodes = collect_inst_nodes(all_edges)

    retrofit_edges = []
    problems = []
    expected_count = sum(len(children) for _, children in PARENT_CHILDREN)

    for parent, children in PARENT_CHILDREN:
        for child in children:
            if child not in inst_nodes:
                problems.append(f"child not in canonical node set: {child!r}")
                continue
            meta = find_source_edge_for_child(child, all_edges)
            if meta is None:
                problems.append(f"no source edge found for child: {child!r}")
                continue
            start_year = meta["start_year"]
            if start_year is None or start_year == 0:
                problems.append(f"invalid start_year for {child!r}: {start_year}")
                continue

            edge = {
                "source_node": child,
                "source_node_type": "institution",
                "target_node": parent,
                "target_node_type": "institution",
                "edge_type": "institutional_parent",
                "start_year": start_year,
                "end_year": 2026,
                "temporal_range": f"{start_year}-ongoing",
                "evidence_citation": meta["evidence_citation"],
                "evidence_type": meta["evidence_type"],
                "evidence_locator": meta["evidence_locator"],
                "confidence": "high",
                "notes": (
                    f"Structural parent-child relationship; child sub-unit operates within "
                    f"parent institution. Ongoing as of 2026. Evidence inherited from "
                    f"{meta['source_desc']}: {meta['evidence_citation']}."
                ),
            }
            retrofit_edges.append(edge)

    if problems:
        print("PROBLEMS detected:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)

    # Validate
    REQUIRED = ["source_node", "source_node_type", "target_node", "target_node_type",
                "edge_type", "start_year", "end_year", "temporal_range",
                "evidence_citation", "evidence_type", "evidence_locator", "confidence"]
    bare_roots = {p for p, _ in PARENT_CHILDREN}
    gate = True
    for i, e in enumerate(retrofit_edges):
        for f in REQUIRED:
            if f not in e or (isinstance(e[f], str) and e[f] == "" and f in ("evidence_citation", "evidence_locator")):
                # Allow empty evidence string? Per spec, evidence fields are required but may be empty
                # if source edge had empty. Flag as warning, not failure.
                if f in ("evidence_citation", "evidence_locator"):
                    print(f"WARN: edge {i} has empty {f}  (inherited from source)", file=sys.stderr)
                else:
                    print(f"FAIL: edge {i} missing field {f}")
                    gate = False
        if e["edge_type"] != "institutional_parent":
            gate = False
            print(f"FAIL: edge {i} wrong type")
        if e["start_year"] > e["end_year"]:
            gate = False
            print(f"FAIL: edge {i} start>end")
        if e["start_year"] == 0 or e["end_year"] == 9999:
            gate = False
            print(f"FAIL: edge {i} sentinel")
        if e["target_node"] not in bare_roots:
            gate = False
            print(f"FAIL: edge {i} target not in bare roots: {e['target_node']}")

    if len(retrofit_edges) != expected_count:
        gate = False
        print(f"FAIL: expected {expected_count} edges, got {len(retrofit_edges)}")

    # Write
    out = ROOT / "15_institutional_hierarchy.json"
    out.write_text(json.dumps(retrofit_edges, indent=2))

    # Re-parse
    json.loads(out.read_text())

    print("\n=== Phase F ===")
    print(f"Edges authored: {len(retrofit_edges)}")
    print(f"Bare roots: {sorted(bare_roots)}")
    print(f"Output: {out.name}")
    print(f"Validation: {'PASS' if gate else 'FAIL'}")
    if not gate:
        sys.exit(1)

    # Summary
    by_parent = {}
    for e in retrofit_edges:
        by_parent.setdefault(e["target_node"], []).append(
            f"{e['source_node']} ({e['start_year']}, {e['evidence_citation'][:30]})"
        )
    print("\nPer-parent edge breakdown:")
    for p in sorted(by_parent):
        print(f"  {p}: {len(by_parent[p])} children")
        for c in by_parent[p]:
            print(f"    - {c}")


if __name__ == "__main__":
    main()
