#!/usr/bin/env python3
"""
V10 Phase B — author institutional_parent retrofit edges + deferred list.
"""

import json
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).parent
MODULES = [
    "01_halsted_core.json", "02_general_surgery_spread.json",
    "03_neurosurgery.json", "04_cardiothoracic_vascular.json",
    "05_urology.json", "06_orthopedics.json",
    "07_oncology_trials.json", "08_subspecialties.json",
    "09_trauma_acute_infection.json", "10_quality_outcomes.json",
    "11_mis_robotic.json", "12_governance_societies.json",
    "13_pre_halsted.json", "14_global_military.json",
]

# (child_name, inferred_parent, routed_module, status_hint)
SUB_INSTITUTIONS = [
    ("Massachusetts General Hospital Thoracic Surgical Service",
     "Massachusetts General Hospital",
     "04_cardiothoracic_vascular.json"),
    ("Mayo Clinic Section of Proctology",
     "Mayo Clinic",
     "08_subspecialties.json"),
    ("Mediterranean Theater Surgical Service",
     None,
     None),
    ("Memorial Sloan Kettering HPB Service",
     "Memorial Sloan Kettering Cancer Center",
     "08_subspecialties.json"),
    ("University of Miami Division of Plastic Surgery",
     "University of Miami",
     "08_subspecialties.json"),
    ("Washington University Chest Service",
     "Washington University",
     None),  # deferred
    ("Washington University Division of Plastic Surgery",
     "Washington University",
     None),  # deferred
    ("Washington University Division of Urologic Surgery",
     "Washington University",
     None),  # deferred
]


def load_all_edges():
    edges_by_module = {}
    for fname in MODULES:
        p = ROOT / fname
        with p.open() as f:
            edges_by_module[fname] = json.load(f)
    return edges_by_module


def collect_institution_nodes(edges_by_module):
    inst_nodes = set()
    for fname, edges in edges_by_module.items():
        for e in edges:
            if e["source_node_type"] == "institution":
                inst_nodes.add(e["source_node"])
            if e["target_node_type"] == "institution":
                inst_nodes.add(e["target_node"])
    return inst_nodes


def find_parent(parent, inst_nodes):
    """Return (canonical_name, method) or (None, None)."""
    if parent is None:
        return None, None
    if parent in inst_nodes:
        return parent, "exact"
    best = (None, 0.0)
    for n in inst_nodes:
        r = SequenceMatcher(None, parent, n).ratio()
        if r > best[1]:
            best = (n, r)
    if best[1] >= 0.92:
        return best[0], f"fuzzy({best[1]:.2f})"
    return None, f"no_match(best={best[0]!r}@{best[1]:.2f})"


def find_founder_edge_for_child(child, edges_by_module):
    """Return (founder_edge, module_fname) or (None, None).
    A 'founder edge' has edge_type == institutional_founder and target_node == child.
    """
    for fname, edges in edges_by_module.items():
        for e in edges:
            if (e["edge_type"] == "institutional_founder"
                    and e["target_node"] == child):
                return e, fname
    return None, None


def main():
    edges_by_module = load_all_edges()
    inst_nodes = collect_institution_nodes(edges_by_module)

    retrofit_edges = []
    deferred = []

    for child, parent, routed_module in SUB_INSTITUTIONS:
        founder_edge, founder_module = find_founder_edge_for_child(child, edges_by_module)

        if parent is None:
            deferred.append({
                "child": child,
                "parent": None,
                "reason": "No clean parent — child is a theater-level organizational unit with no standing parent institution in the graph. Defer pending V10 review.",
                "founder_edge": bool(founder_edge),
                "founder_module": founder_module,
            })
            continue

        canonical_parent, method = find_parent(parent, inst_nodes)
        if canonical_parent is None:
            deferred.append({
                "child": child,
                "parent": parent,
                "reason": f"Parent node '{parent}' not yet in graph ({method}). Pending V10 authorship of parent department.",
                "founder_edge": bool(founder_edge),
                "founder_module": founder_module,
            })
            continue

        # Parent exists — author retrofit edge
        if founder_edge is None:
            deferred.append({
                "child": child,
                "parent": canonical_parent,
                "reason": "No founder edge exists for child; cannot reuse evidence. Manual evidence sourcing required.",
                "founder_edge": False,
                "founder_module": None,
            })
            continue

        start_year = founder_edge.get("start_year")
        # Reuse citation + locator from founder edge
        citation = founder_edge.get("evidence_citation", "")
        etype = founder_edge.get("evidence_type", "institutional_archive")
        locator = founder_edge.get("evidence_locator", "")

        # Determine routed module per spec (override to founder module if spec's
        # routed_module is None but founder_module is set — but spec is explicit,
        # so trust the spec mapping)
        route = routed_module if routed_module else founder_module

        retrofit_edge = {
            "source_node": child,
            "source_node_type": "institution",
            "target_node": canonical_parent,
            "target_node_type": "institution",
            "edge_type": "institutional_parent",
            "start_year": start_year,
            "end_year": 2026,
            "temporal_range": f"{start_year}-ongoing",
            "evidence_citation": citation,
            "evidence_type": etype,
            "evidence_locator": locator,
            "confidence": "high",
            "notes": (
                f"Structural parent-child relationship. Ongoing as of 2026. "
                f"Evidence reused from founder edge: {citation}. "
                f"Parent matched via {method}. "
                f"Routed to module: {route}."
            ),
        }
        retrofit_edges.append(retrofit_edge)

    # Write retrofit JSON
    retrofit_path = ROOT / "v10_institutional_parent_retrofit.json"
    with retrofit_path.open("w") as f:
        json.dump(retrofit_edges, f, indent=2)

    # Write deferred markdown
    deferred_path = ROOT / "v10_retrofit_deferred.md"
    md = ["# V10 Institutional Parent Retrofit — Deferred List", ""]
    md.append(f"Generated during Phase B. {len(deferred)} sub-institution(s) deferred.")
    md.append("")
    md.append("## Deferred sub-institutions")
    md.append("")
    md.append("| # | Child sub-institution | Inferred parent | Reason |")
    md.append("|---|---|---|---|")
    for i, d in enumerate(deferred, 1):
        p = d["parent"] if d["parent"] else "_(no clean parent)_"
        md.append(f"| {i} | {d['child']} | {p} | {d['reason']} |")
    md.append("")
    md.append("## Routing notes")
    md.append("")
    md.append("All deferred cases require V10 departmental authorship of the parent "
              "institution node before an `institutional_parent` edge can be authored. "
              "The Mediterranean Theater Surgical Service case is a separate class: "
              "it has no standing parent institution in the graph and may need a "
              "different structural modeling approach.")
    md.append("")
    deferred_path.write_text("\n".join(md))

    # Validation
    print("=" * 60)
    print("PHASE B RESULTS")
    print("=" * 60)
    print(f"Retrofit edges authored: {len(retrofit_edges)}")
    print(f"Deferred cases: {len(deferred)}")
    print()
    print("Retrofit edges:")
    for e in retrofit_edges:
        print(f"  {e['source_node']}")
        print(f"    → {e['target_node']} ({e['temporal_range']})")
        print(f"    evidence: {e['evidence_citation']}")
    print()
    print("Deferred:")
    for d in deferred:
        print(f"  {d['child']}")
        print(f"    parent: {d['parent']}")
        print(f"    reason: {d['reason']}")
    print()

    # Validation gate checks
    REQUIRED_FIELDS = [
        "source_node", "source_node_type", "target_node", "target_node_type",
        "edge_type", "start_year", "end_year", "temporal_range",
        "evidence_citation", "evidence_type", "evidence_locator", "confidence"
    ]
    gate_pass = True
    for i, e in enumerate(retrofit_edges):
        for f in REQUIRED_FIELDS:
            if f not in e:
                print(f"FAIL: edge {i} missing field {f}")
                gate_pass = False
        if e["edge_type"] != "institutional_parent":
            print(f"FAIL: edge {i} wrong edge_type {e['edge_type']}")
            gate_pass = False
        if e["target_node"] not in inst_nodes:
            print(f"FAIL: edge {i} target_node {e['target_node']!r} not in canonical set")
            gate_pass = False
        if e["start_year"] > e["end_year"]:
            print(f"FAIL: edge {i} start>end")
            gate_pass = False
    if len(deferred) < 4:
        print(f"FAIL: only {len(deferred)} deferred cases (expected ≥4)")
        gate_pass = False

    # Re-parse retrofit JSON
    try:
        json.loads(retrofit_path.read_text())
    except Exception as e:
        print(f"FAIL: retrofit file does not parse: {e}")
        gate_pass = False

    print()
    print("Phase B validation:", "PASS" if gate_pass else "FAIL")
    if not gate_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
