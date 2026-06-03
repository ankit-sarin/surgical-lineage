#!/usr/bin/env python3
"""
V10 Pre-Retrofit Diagnostic Audit
Read-only audit of the 14 module files. Produces V11_diagnostic_audit_report.md.
"""

import json
import sys
import re
from collections import defaultdict, Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).parent
EXPECTED_MODULES = [
    "01_halsted_core.json",
    "02_general_surgery_spread.json",
    "03_neurosurgery.json",
    "04_cardiothoracic_vascular.json",
    "05_urology.json",
    "06_orthopedics.json",
    "07_oncology_trials.json",
    "08_subspecialties.json",
    "09_trauma_acute_infection.json",
    "10_quality_outcomes.json",
    "11_mis_robotic.json",
    "12_governance_societies.json",
    "13_pre_halsted.json",
    "14_global_military.json",
    "15_institutional_hierarchy.json",
]
BASELINE_EDGES = 525
BASELINE_NODES = 403

PERSON_SIM_THRESHOLD = 0.88
INSTITUTION_SIM_THRESHOLD = 0.85
SOCIETY_SIM_THRESHOLD = 0.88
MIDDLE_INITIAL_RE = re.compile(r"\b[A-Z]\.?\b")

REPORT_PATH = ROOT / "V12_diagnostic_audit_report.md"


def load_modules():
    """Load all 14 module files. Returns list of (module_label, edges, path)."""
    loaded = []
    missing = []
    for fname in EXPECTED_MODULES:
        p = ROOT / fname
        if not p.exists():
            missing.append(fname)
            continue
        try:
            with p.open() as f:
                edges = json.load(f)
        except json.JSONDecodeError as e:
            sys.exit(f"ABORT: {fname} failed to parse as JSON — {e}")
        if not isinstance(edges, list):
            sys.exit(f"ABORT: {fname} top-level is not a list")
        label = fname.split("_")[0]  # "01", "02", ...
        loaded.append((label, edges, fname))
    if missing:
        print(f"WARNING: missing module files: {missing}", file=sys.stderr)
    return loaded, missing


def collect_nodes(modules):
    """Return dict (name, type) -> set of module labels where it appears."""
    node_modules = defaultdict(set)
    for label, edges, _ in modules:
        for e in edges:
            node_modules[(e["source_node"], e["source_node_type"])].add(label)
            node_modules[(e["target_node"], e["target_node_type"])].add(label)
    return node_modules


def differs_only_by_middle_initial(a, b):
    """Return True if a and b differ only by presence/absence of middle initials."""
    strip_a = MIDDLE_INITIAL_RE.sub("", a).strip()
    strip_a = re.sub(r"\s+", " ", strip_a)
    strip_b = MIDDLE_INITIAL_RE.sub("", b).strip()
    strip_b = re.sub(r"\s+", " ", strip_b)
    return strip_a == strip_b and a != b


def audit_1_canonical_names(node_modules):
    persons, institutions, societies = [], [], []
    for (name, ntype) in node_modules:
        if ntype == "person":
            persons.append(name)
        elif ntype == "institution":
            institutions.append(name)
        elif ntype == "society":
            societies.append(name)

    def pairwise(names, threshold, downweight_middle_initial=False):
        flagged = []
        for i, a in enumerate(sorted(names)):
            for b in sorted(names)[i + 1:]:
                ratio = SequenceMatcher(None, a, b).ratio()
                if ratio >= threshold and ratio < 1.0:
                    note = ""
                    if downweight_middle_initial and differs_only_by_middle_initial(a, b):
                        note = "differs only by middle initial — likely variant or distinct person"
                    flagged.append((a, b, ratio, note))
        return flagged

    person_pairs = pairwise(persons, PERSON_SIM_THRESHOLD, downweight_middle_initial=True)
    institution_pairs = pairwise(institutions, INSTITUTION_SIM_THRESHOLD)
    society_pairs = pairwise(societies, SOCIETY_SIM_THRESHOLD)

    def mod_list(name, ntype):
        return ", ".join(sorted(node_modules[(name, ntype)]))

    lines = ["## Audit 1 — Canonical Name Similarity", ""]
    for title, pairs, ntype in [
        ("Persons", person_pairs, "person"),
        ("Institutions", institution_pairs, "institution"),
        ("Societies", society_pairs, "society"),
    ]:
        lines.append(f"### {title} ({len(pairs)} pairs flagged)")
        lines.append("")
        if not pairs:
            lines.append("_None flagged._")
            lines.append("")
            continue
        lines.append("| Name A | Name B | Ratio | Modules A | Modules B | Note | Verdict |")
        lines.append("|---|---|---|---|---|---|---|")
        for a, b, r, note in sorted(pairs, key=lambda x: -x[2]):
            lines.append(
                f"| {a} | {b} | {r:.2f} | {mod_list(a, ntype)} | {mod_list(b, ntype)} | {note} | MANUAL REVIEW |"
            )
        lines.append("")

    return lines, {
        "person_pairs": len(person_pairs),
        "institution_pairs": len(institution_pairs),
        "society_pairs": len(society_pairs),
        "institution_high_ratio": sum(1 for _, _, r, _ in institution_pairs if r >= 0.95),
    }


def audit_2_temporal(modules):
    sentinel_rows = []
    inversion_rows = []
    same_year_rows = []  # for direct_training / governance_leadership
    start_year_counter = Counter()
    end_year_counter = Counter()
    total_edges = 0

    RANGED_TYPES = {"direct_training", "governance_leadership"}

    for label, edges, _ in modules:
        for e in edges:
            total_edges += 1
            sy, ey = e.get("start_year"), e.get("end_year")
            start_year_counter[sy] += 1
            end_year_counter[ey] += 1
            flags = []
            if sy == 0 or ey == 0:
                flags.append("zero sentinel")
            if sy == 9999 or ey == 9999:
                flags.append("9999 sentinel")
            if isinstance(sy, int) and sy < 1700 and sy != 0:
                flags.append(f"start_year < 1700 ({sy})")
            if isinstance(ey, int) and ey > 2030 and ey != 9999:
                flags.append(f"end_year > 2030 ({ey})")
            if flags:
                sentinel_rows.append((label, e["source_node"], e["target_node"],
                                      e["edge_type"], sy, ey, "; ".join(flags)))
            if isinstance(sy, int) and isinstance(ey, int) and sy != 0 and ey != 0 and sy > ey:
                inversion_rows.append((label, e["source_node"], e["target_node"],
                                       e["edge_type"], sy, ey))
            if (isinstance(sy, int) and isinstance(ey, int)
                    and sy == ey and sy != 0 and e["edge_type"] in RANGED_TYPES):
                same_year_rows.append((label, e["source_node"], e["target_node"],
                                       e["edge_type"], sy, ey))

    # round-year clusters
    round_years = [1800, 1850, 1900, 1950, 2000]
    round_cluster = []
    for ry in round_years:
        sc = start_year_counter.get(ry, 0)
        ec = end_year_counter.get(ry, 0)
        start_pct = (sc / total_edges * 100) if total_edges else 0
        end_pct = (ec / total_edges * 100) if total_edges else 0
        unusual = "FLAG" if (start_pct > 3.0 or end_pct > 3.0) else ""
        round_cluster.append((ry, sc, ec, start_pct, end_pct, unusual))

    lines = ["## Audit 2 — Temporal Anomalies", ""]

    lines.append(f"### Sentinel / out-of-range values ({len(sentinel_rows)} edges)")
    lines.append("")
    if sentinel_rows:
        lines.append("| Module | Source | Target | Edge Type | start_year | end_year | Flag |")
        lines.append("|---|---|---|---|---|---|---|")
        for r in sentinel_rows:
            lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} |")
    else:
        lines.append("_None flagged._")
    lines.append("")

    lines.append(f"### Logical inversions (start > end, {len(inversion_rows)} edges)")
    lines.append("")
    if inversion_rows:
        lines.append("| Module | Source | Target | Edge Type | start_year | end_year |")
        lines.append("|---|---|---|---|---|---|")
        for r in inversion_rows:
            lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |")
    else:
        lines.append("_None flagged._")
    lines.append("")

    lines.append(f"### Same-year edges on ranged types ({len(same_year_rows)} edges — verify brief tenure vs data error)")
    lines.append("")
    if same_year_rows:
        lines.append("| Module | Source | Target | Edge Type | Year |")
        lines.append("|---|---|---|---|---|")
        for r in same_year_rows:
            lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")
    else:
        lines.append("_None flagged._")
    lines.append("")

    lines.append("### Round-year clusters (flag if >3% of total edges)")
    lines.append("")
    lines.append("| Year | As start_year | As end_year | start % | end % | Flag |")
    lines.append("|---|---|---|---|---|---|")
    for ry, sc, ec, sp, ep, flag in round_cluster:
        lines.append(f"| {ry} | {sc} | {ec} | {sp:.1f}% | {ep:.1f}% | {flag} |")
    lines.append("")

    return lines, {
        "sentinels": len(sentinel_rows),
        "inversions": len(inversion_rows),
        "same_year": len(same_year_rows),
        "round_clusters_flagged": sum(1 for *_, f in round_cluster if f),
    }


def audit_3_dedup(modules):
    # Check A — literal duplicates
    triplet_groups = defaultdict(list)  # key -> [(module, edge), ...]
    pair_groups = defaultdict(list)     # (source, target) -> [(module, edge), ...]
    for label, edges, _ in modules:
        for e in edges:
            k = (e["source_node"], e["target_node"], e["edge_type"])
            triplet_groups[k].append((label, e))
            pair_groups[(e["source_node"], e["target_node"])].append((label, e))

    literal_dups = [(k, v) for k, v in triplet_groups.items() if len(v) > 1]

    # Check B — same source+target with multiple edge types
    multi_type_pairs = []
    for (s, t), items in pair_groups.items():
        types = {entry[1]["edge_type"] for entry in items}
        if len(types) > 1:
            multi_type_pairs.append((s, t, items))

    # Check C — multi-governance at same institution
    gov_groups = defaultdict(list)
    for label, edges, _ in modules:
        for e in edges:
            if (e["edge_type"] == "governance_leadership"
                    and e["source_node_type"] == "person"
                    and e["target_node_type"] == "institution"):
                gov_groups[(e["source_node"], e["target_node"])].append((label, e))
    multi_gov = [(k, v) for k, v in gov_groups.items() if len(v) > 1]

    def year_overlap(a, b):
        """Return True if two (sy, ey) tuples overlap or are identical."""
        a_sy, a_ey = a
        b_sy, b_ey = b
        if None in (a_sy, a_ey, b_sy, b_ey):
            return False
        if a_sy == b_sy and a_ey == b_ey:
            return True
        return not (a_ey < b_sy or b_ey < a_sy)

    lines = ["## Audit 3 — Dedup Discipline", ""]

    # A
    lines.append(f"### Check A — literal (source, target, edge_type) duplicates ({len(literal_dups)} groups)")
    lines.append("")
    lines.append("_Expected: zero rows. Any rows = merge pipeline failure._")
    lines.append("")
    if literal_dups:
        lines.append("| Modules | Source | Target | Edge Type | Count |")
        lines.append("|---|---|---|---|---|")
        for (s, t, et), items in literal_dups:
            mods = ", ".join(sorted({lbl for lbl, _ in items}))
            lines.append(f"| {mods} | {s} | {t} | {et} | {len(items)} |")
    else:
        lines.append("_No literal duplicates found._")
    lines.append("")

    # B
    lines.append(f"### Check B — same source→target with multiple edge_types ({len(multi_type_pairs)} pairs)")
    lines.append("")
    if multi_type_pairs:
        lines.append("| Source | Target | Edge Types | Temporal Ranges | Modules | Review |")
        lines.append("|---|---|---|---|---|---|")
        for s, t, items in sorted(multi_type_pairs, key=lambda x: (x[0], x[1])):
            types = "; ".join(sorted({e["edge_type"] for _, e in items}))
            ranges = "; ".join(sorted({e.get("temporal_range", "") for _, e in items}))
            mods = ", ".join(sorted({lbl for lbl, _ in items}))
            lines.append(f"| {s} | {t} | {types} | {ranges} | {mods} | MANUAL REVIEW |")
    else:
        lines.append("_None found._")
    lines.append("")

    # C
    overlap_count = 0
    lines.append(f"### Check C — multi-governance_leadership to same institution ({len(multi_gov)} person↔institution pairs)")
    lines.append("")
    if multi_gov:
        lines.append("| Person | Institution | Tenures | Overlap? | Modules |")
        lines.append("|---|---|---|---|---|")
        for (person, inst), items in sorted(multi_gov, key=lambda x: (x[0][0], x[0][1])):
            tenures = []
            for _, e in items:
                tenures.append((e.get("start_year"), e.get("end_year")))
            tenure_strs = "; ".join(
                f"{e.get('temporal_range','?')}" for _, e in items
            )
            overlap = "NO"
            for i in range(len(tenures)):
                for j in range(i + 1, len(tenures)):
                    if year_overlap(tenures[i], tenures[j]):
                        overlap = "YES — review"
                        break
                if overlap != "NO":
                    break
            if overlap != "NO":
                overlap_count += 1
            mods = ", ".join(sorted({lbl for lbl, _ in items}))
            lines.append(f"| {person} | {inst} | {tenure_strs} | {overlap} | {mods} |")
    else:
        lines.append("_None found._")
    lines.append("")

    return lines, {
        "literal_dups": len(literal_dups),
        "multi_type_pairs": len(multi_type_pairs),
        "multi_gov": len(multi_gov),
        "multi_gov_overlap": overlap_count,
    }


def main():
    modules, missing = load_modules()
    total_edges = sum(len(edges) for _, edges, _ in modules)
    node_modules = collect_nodes(modules)
    unique_nodes = len(node_modules)

    # Connectivity (phase_h pattern): simple undirected graph over all edges.
    G = nx.Graph()
    for _, edges, _ in modules:
        for e in edges:
            G.add_edge(e["source_node"], e["target_node"])
    n_components = nx.number_connected_components(G)

    baseline_note = ""
    if total_edges != BASELINE_EDGES:
        baseline_note += f"⚠️  Edge count {total_edges} differs from baseline {BASELINE_EDGES}.\n"
    if unique_nodes != BASELINE_NODES:
        baseline_note += f"⚠️  Unique node count {unique_nodes} differs from baseline {BASELINE_NODES}.\n"
    if n_components != 1:
        baseline_note += f"⚠️  Connected components {n_components} != 1 (graph is fragmented).\n"
    if missing:
        baseline_note += f"⚠️  Missing module files: {missing}\n"

    a1_lines, a1_stats = audit_1_canonical_names(node_modules)
    a2_lines, a2_stats = audit_2_temporal(modules)
    a3_lines, a3_stats = audit_3_dedup(modules)

    # Recommended next steps heuristics
    next_steps = []
    if a3_stats["literal_dups"] > 0:
        next_steps.append(
            f"**BLOCKING**: {a3_stats['literal_dups']} literal-duplicate edge group(s) in Audit 3 Check A "
            "must be resolved before V10 retrofit (merge pipeline failure)."
        )
    if a1_stats["institution_high_ratio"] > 0:
        next_steps.append(
            f"Recommend canonical-name adjudication for {a1_stats['institution_high_ratio']} "
            "institution pair(s) with similarity ≥ 0.95 before retrofit — institutional_parent naming "
            "depends on canonical choice."
        )
    if a2_stats["inversions"] > 0:
        next_steps.append(
            f"Fix {a2_stats['inversions']} temporal inversion(s) (start_year > end_year) before retrofit."
        )
    if a2_stats["sentinels"] > 0:
        next_steps.append(
            f"Review {a2_stats['sentinels']} edge(s) with sentinel or out-of-range temporal values."
        )
    if a3_stats["multi_gov_overlap"] > 0:
        next_steps.append(
            f"Review {a3_stats['multi_gov_overlap']} overlapping governance_leadership tenure(s) — "
            "likely data-entry duplicates masquerading as role transitions."
        )
    if not next_steps:
        next_steps.append("Zero blocking issues surfaced — proceed with V10 retrofit (Task 2).")

    # Build summary header
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = [
        "# V12 Pre-Retrofit Diagnostic Audit",
        f"Generated: {ts}",
        f"Graph state: {total_edges} edges across {len(modules)} module files, "
        f"{unique_nodes} unique nodes, {n_components} connected component(s)",
        "",
    ]
    if baseline_note:
        header.append("## Baseline discrepancies")
        header.append("")
        header.append(baseline_note)
        header.append("")

    header += [
        "## Summary of findings",
        f"- **Audit 1 (Canonical Names):** {a1_stats['person_pairs']} person pair(s), "
        f"{a1_stats['institution_pairs']} institution pair(s), "
        f"{a1_stats['society_pairs']} society pair(s) flagged "
        f"(institution pairs ≥ 0.95: {a1_stats['institution_high_ratio']})",
        f"- **Audit 2 (Temporal):** {a2_stats['sentinels']} sentinel/out-of-range, "
        f"{a2_stats['inversions']} logical inversion(s), "
        f"{a2_stats['same_year']} same-year ranged edge(s), "
        f"{a2_stats['round_clusters_flagged']} round-year cluster(s) flagged",
        f"- **Audit 3 (Dedup):** {a3_stats['literal_dups']} literal duplicate group(s), "
        f"{a3_stats['multi_type_pairs']} multi-type pair(s), "
        f"{a3_stats['multi_gov']} multi-governance case(s) "
        f"(overlapping: {a3_stats['multi_gov_overlap']})",
        "",
        "## Recommended next steps",
    ]
    for step in next_steps:
        header.append(f"- {step}")
    header.append("")
    header.append("---")
    header.append("")

    out = "\n".join(header + a1_lines + ["---", ""] + a2_lines + ["---", ""] + a3_lines)
    REPORT_PATH.write_text(out)
    print(f"Wrote {REPORT_PATH}")
    print(f"  Edges: {total_edges}  Nodes: {unique_nodes}  "
          f"Components: {n_components}  Modules loaded: {len(modules)}")


if __name__ == "__main__":
    main()
