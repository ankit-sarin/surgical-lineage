#!/usr/bin/env python3
"""
Unified Diagnostic Audit — read-only audit of the module files.

Same three audits as v10_diagnostic_audit.py (canonical-name similarity, temporal anomalies,
dedup discipline), preserved verbatim. Differences:
  - module list, paths come from --config (no hardcoded EXPECTED_MODULES),
  - report path + title are derived from --version (no hardcoded REPORT_PATH),
  - no hardcoded BASELINE_EDGES/NODES,
  - the config name_pair_whitelist suppresses known-distinct name pairs from Audit 1,
  - the still-useful figures from the retired v10_retrofit_report.md (module inventory,
    edge-type distribution, label-file counts) are folded in as a "Graph composition" section.
"""
import argparse
import json
import sys
import re
from collections import defaultdict, Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

import networkx as nx

PERSON_SIM_THRESHOLD = 0.88
INSTITUTION_SIM_THRESHOLD = 0.85
SOCIETY_SIM_THRESHOLD = 0.88
MIDDLE_INITIAL_RE = re.compile(r"\b[A-Z]\.?\b")

# --- residency_at gating (schema v3.1) ------------------------------------------------------
# Every residency_at edge must carry exactly one [residency_at_reason: X] token whose X names
# why no qualifying person endpoint exists. Zero tokens, two-or-more tokens, or an off-list X
# is a BLOCKING finding. Non-residency_at edges are never checked.
# director-unidentified vs preceptor-untitled: director-unidentified means the preceptor is
# UNKNOWN (a direct_training-first search found no identifiable PD/APD); preceptor-untitled means
# the preceptor IS identified by name but holds NO documented structural title (chair / chief /
# program director / associate program director), so no direct_training edge is warranted.
RESIDENCY_REASONS = {"mentorless-by-committee", "pre-PD-era", "director-unidentified",
                     "preceptor-untitled"}
RESIDENCY_TOKEN_RE = re.compile(r"\[residency_at_reason:\s*([^\]]*?)\s*\]")

# Name-suffix tokens (period-stripped, lowercased) that must MATCH for a person-variant flag.
NAME_SUFFIXES = {"jr", "sr", "ii", "iii", "iv"}


def residency_token_finding(edge):
    """Return a blocking-reason string for a residency_at edge that violates the token rule,
    else None. Edges of any other edge_type return None (never checked)."""
    if edge.get("edge_type") != "residency_at":
        return None
    tokens = RESIDENCY_TOKEN_RE.findall(edge.get("notes", "") or "")
    if len(tokens) == 0:
        return "missing [residency_at_reason: X] token"
    if len(tokens) > 1:
        return f"{len(tokens)} [residency_at_reason: X] tokens found (expected exactly 1)"
    x = tokens[0]
    if x not in RESIDENCY_REASONS:
        return (f"off-list residency_at_reason {x!r} "
                f"(allowed: {', '.join(sorted(RESIDENCY_REASONS))})")
    return None


def _parse_person_name(name):
    """Split a person name into (first, middle_tokens, last, suffix). first/last/suffix are
    lowercased; suffix is period-stripped or None. Middle tokens keep original case."""
    toks = name.split()
    suffix = None
    if toks and toks[-1].lower().rstrip(".") in NAME_SUFFIXES:
        suffix = toks[-1].lower().rstrip(".")
        toks = toks[:-1]
    if not toks:
        return "", [], "", suffix
    first = toks[0].lower()
    last = toks[-1].lower()
    middle = toks[1:-1] if len(toks) > 2 else []
    return first, middle, last, suffix


def _middle_compatible(ma, mb):
    """True iff two (differing) middle-token lists are the same underlying middle in different
    representation: one side absent (present-vs-absent), or an aligned initial-vs-full
    abbreviation (e.g. ['M.'] vs ['McDowell']). Two distinct middle initials/names (A. vs B.,
    McDowell vs Aloysius) are different people → False."""
    if not ma or not mb:
        return True  # present vs absent
    if len(ma) != len(mb):
        return False
    for x, y in zip(ma, mb):
        x0, y0 = x.rstrip(".").lower(), y.rstrip(".").lower()
        if x0 == y0:
            continue
        if len(x0) == 1 and y0[:1] == x0:  # x is the initial of full-name y
            continue
        if len(y0) == 1 and x0[:1] == y0:  # y is the initial of full-name x
            continue
        return False
    return True


def person_name_variant(a, b):
    """True iff a and b are a same-person name-representation variant: identical first and last
    name tokens, matching suffix (present-vs-absent or differing suffix never flags), and a
    middle representation that DIFFERS but is compatible (initial vs full, or present vs absent).
    Differing surnames, differing first names, or genuinely different middles never flag.
    Identical strings are not a pair."""
    if a == b:
        return False
    fa, ma, la, sa = _parse_person_name(a)
    fb, mb, lb, sb = _parse_person_name(b)
    if not fa or not la:
        return False
    if fa != fb or la != lb:
        return False
    if sa != sb:
        return False
    if [m.lower() for m in ma] == [m.lower() for m in mb]:
        return False  # middle representation identical → not a variant
    return _middle_compatible(ma, mb)


def structural_person_variants(names):
    """Return sorted list of (a, b) person-name variant pairs per person_name_variant()."""
    names = sorted(names)
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if person_name_variant(a, b):
                pairs.append((a, b))
    return pairs


def load_config(config_path):
    cfg = json.loads(Path(config_path).read_text())
    base = Path(config_path).resolve().parent
    cfg["_base"] = base
    cfg["_modules_dir"] = (base / cfg["paths"]["modules_dir"]).resolve()
    cfg["_node_labels"] = (base / cfg["paths"]["node_labels"]).resolve()
    cfg["_reports_dir"] = (base / cfg["paths"]["reports_dir"]).resolve()
    return cfg


def load_modules(modules_dir, route_map):
    """Load module files named in the config route map. Returns [(label, edges, fname)]."""
    loaded = []
    missing = []
    for fname in sorted(route_map.values()):
        p = modules_dir / fname
        if not p.exists():
            missing.append(fname)
            continue
        try:
            edges = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            sys.exit(f"ABORT: {fname} failed to parse as JSON — {e}")
        if not isinstance(edges, list):
            sys.exit(f"ABORT: {fname} top-level is not a list")
        label = fname.split("_")[0]
        loaded.append((label, edges, fname))
    if missing:
        print(f"WARNING: missing module files: {missing}", file=sys.stderr)
    return loaded, missing


def collect_nodes(modules):
    node_modules = defaultdict(set)
    for label, edges, _ in modules:
        for e in edges:
            node_modules[(e["source_node"], e["source_node_type"])].add(label)
            node_modules[(e["target_node"], e["target_node_type"])].add(label)
    return node_modules


def differs_only_by_middle_initial(a, b):
    strip_a = MIDDLE_INITIAL_RE.sub("", a).strip()
    strip_a = re.sub(r"\s+", " ", strip_a)
    strip_b = MIDDLE_INITIAL_RE.sub("", b).strip()
    strip_b = re.sub(r"\s+", " ", strip_b)
    return strip_a == strip_b and a != b


def audit_1_canonical_names(node_modules, whitelist):
    persons, institutions, societies = [], [], []
    for (name, ntype) in node_modules:
        if ntype == "person":
            persons.append(name)
        elif ntype == "institution":
            institutions.append(name)
        elif ntype == "society":
            societies.append(name)

    # T1.4 — suppression accounting. `suppressed` records EVERY whitelist-suppressed pair,
    # keyed by frozenset so a pair found by both detectors is one entry carrying both tags.
    # Before T1.4 only the fuzzy-ratio detector recorded its suppressions here; the token
    # detector dropped whitelisted pairs silently (so "Whitelisted name pairs: N" under-reported
    # — at V17-B2 it read 1, hiding the whitelisted Warren pair the token rule had caught).
    # "Whitelisted name pairs: N" now means actively-suppressed pairs, full stop.
    suppressed = {}

    def record_suppressed(a, b, ratio, detector):
        key = frozenset({a, b})
        entry = suppressed.get(key)
        if entry is None:
            suppressed[key] = {"a": a, "b": b, "ratio": ratio,
                               "reason": whitelist[key], "detectors": [detector]}
        elif detector not in entry["detectors"]:
            entry["detectors"].append(detector)

    def pairwise(names, threshold, downweight_middle_initial=False):
        flagged = []
        for i, a in enumerate(sorted(names)):
            for b in sorted(names)[i + 1:]:
                ratio = SequenceMatcher(None, a, b).ratio()
                if ratio >= threshold and ratio < 1.0:
                    if frozenset({a, b}) in whitelist:
                        record_suppressed(a, b, ratio, "fuzzy")
                        continue
                    note = ""
                    if downweight_middle_initial and differs_only_by_middle_initial(a, b):
                        note = "differs only by middle initial — likely variant or distinct person"
                    flagged.append((a, b, ratio, note, ["fuzzy"]))
        return flagged

    person_pairs = pairwise(persons, PERSON_SIM_THRESHOLD, downweight_middle_initial=True)
    institution_pairs = pairwise(institutions, INSTITUTION_SIM_THRESHOLD)
    society_pairs = pairwise(societies, SOCIETY_SIM_THRESHOLD)

    # Hardened person-name heuristic: structural same-first/last, suffix-matched, middle-differs
    # variants that the SequenceMatcher ratio gate misses (e.g. "Joseph M. Mathews" vs
    # "Joseph McDowell Mathews", ratio 0.80). The reported person set is the whitelist-filtered
    # UNION of this token detector and the fuzzy-ratio detector above.
    #
    # structural_person_variants() is the single source of truth for the token rule —
    # test_v16_pr.py::test_canonical_person_sweep_finds_no_unresolved_duplicates imports this
    # same function and applies the same whitelist filter (keep the two in step).
    person_index = {frozenset({a, b}): i for i, (a, b, _, _, _) in enumerate(person_pairs)}
    for a, b in structural_person_variants(persons):
        key = frozenset({a, b})
        if key in whitelist:
            # T1.4: whitelisted, so still suppressed — but now COUNTED and tagged, not dropped.
            record_suppressed(a, b, SequenceMatcher(None, a, b).ratio(), "token")
            continue
        if key in person_index:
            # Found by both detectors: tag the existing row rather than duplicating it.
            i = person_index[key]
            a0, b0, r0, note0, dets = person_pairs[i]
            if "token" not in dets:
                person_pairs[i] = (a0, b0, r0, note0, dets + ["token"])
            continue
        person_pairs.append((a, b, SequenceMatcher(None, a, b).ratio(),
                             "middle-name variant (same first/last token, suffix-matched) — "
                             "likely same person; verify vs distinct individual", ["token"]))
        person_index[key] = len(person_pairs) - 1

    def mod_list(name, ntype):
        return ", ".join(sorted(node_modules[(name, ntype)]))

    lines = ["## Audit 1 — Canonical Name Similarity", ""]
    lines.append("Person pairs are the whitelist-filtered UNION of two detectors: `fuzzy` "
                 "(SequenceMatcher ratio ≥ threshold) and `token` (same first/last token, "
                 "suffix-matched, middle differs). Every reported and every suppressed pair is "
                 "tagged with the detector(s) that found it. A pair no detector fires on cannot "
                 "appear here at all, whitelisted or not.")
    lines.append("")
    if suppressed:
        lines.append(f"**Whitelisted (known-distinct, suppressed): {len(suppressed)} pair(s).** "
                     "Suppressed pairs are warn-level context, never blocking.")
        lines.append("")
        for s in sorted(suppressed.values(), key=lambda s: -s["ratio"]):
            lines.append(f"- `{s['a']}` ≈ `{s['b']}` ({s['ratio']:.2f}) "
                         f"[detector: {'+'.join(s['detectors'])}; whitelisted]"
                         + (f" — {s['reason']}" if s["reason"] else ""))
        lines.append("")
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
        lines.append("| Name A | Name B | Ratio | Detector | Modules A | Modules B | Note | Verdict |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for a, b, r, note, dets in sorted(pairs, key=lambda x: -x[2]):
            lines.append(
                f"| {a} | {b} | {r:.2f} | {'+'.join(dets)} | {mod_list(a, ntype)} | "
                f"{mod_list(b, ntype)} | {note} | MANUAL REVIEW |"
            )
        lines.append("")

    return lines, {
        "person_pairs": len(person_pairs),
        "institution_pairs": len(institution_pairs),
        "society_pairs": len(society_pairs),
        "institution_high_ratio": sum(1 for _, _, r, _, _ in institution_pairs if r >= 0.95),
        "suppressed": len(suppressed),
        # Detector attribution, so a future run can tell WHICH heuristic is carrying the load.
        "person_pairs_by_detector": dict(Counter(
            "+".join(dets) for _, _, _, _, dets in person_pairs)),
        "suppressed_by_detector": dict(Counter(
            "+".join(s["detectors"]) for s in suppressed.values())),
    }


def audit_2_temporal(modules):
    sentinel_rows = []
    inversion_rows = []
    same_year_rows = []
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
    triplet_groups = defaultdict(list)
    pair_groups = defaultdict(list)
    for label, edges, _ in modules:
        for e in edges:
            k = (e["source_node"], e["target_node"], e["edge_type"])
            triplet_groups[k].append((label, e))
            pair_groups[(e["source_node"], e["target_node"])].append((label, e))

    literal_dups = [(k, v) for k, v in triplet_groups.items() if len(v) > 1]

    multi_type_pairs = []
    for (s, t), items in pair_groups.items():
        types = {entry[1]["edge_type"] for entry in items}
        if len(types) > 1:
            multi_type_pairs.append((s, t, items))

    gov_groups = defaultdict(list)
    for label, edges, _ in modules:
        for e in edges:
            if (e["edge_type"] == "governance_leadership"
                    and e["source_node_type"] == "person"
                    and e["target_node_type"] == "institution"):
                gov_groups[(e["source_node"], e["target_node"])].append((label, e))
    multi_gov = [(k, v) for k, v in gov_groups.items() if len(v) > 1]

    def year_overlap(a, b):
        a_sy, a_ey = a
        b_sy, b_ey = b
        if None in (a_sy, a_ey, b_sy, b_ey):
            return False
        if a_sy == b_sy and a_ey == b_ey:
            return True
        return not (a_ey < b_sy or b_ey < a_sy)

    lines = ["## Audit 3 — Dedup Discipline", ""]

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
            tenure_strs = "; ".join(f"{e.get('temporal_range','?')}" for _, e in items)
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


def audit_4_residency(modules):
    """Audit 4 — residency_at token gate (schema v3.1). Every residency_at edge must carry
    exactly one valid [residency_at_reason: X] token; violations are BLOCKING."""
    residency_edges = 0
    findings = []  # (label, source, target, reason)
    for label, edges, _ in modules:
        for e in edges:
            if e.get("edge_type") != "residency_at":
                continue
            residency_edges += 1
            reason = residency_token_finding(e)
            if reason:
                findings.append((label, e["source_node"], e["target_node"], reason))

    lines = ["## Audit 4 — residency_at Token Gate", ""]
    lines.append(f"residency_at edges checked: {residency_edges} "
                 f"(allowed reasons: {', '.join(sorted(RESIDENCY_REASONS))})")
    lines.append("")
    lines.append(f"### Blocking token violations ({len(findings)} edges)")
    lines.append("")
    if findings:
        lines.append("| Module | Source | Target | Violation |")
        lines.append("|---|---|---|---|")
        for r in findings:
            lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")
    else:
        lines.append("_No violations._")
    lines.append("")

    return lines, {
        "residency_edges": residency_edges,
        "residency_findings": len(findings),
    }


def composition_section(modules, node_labels_path):
    """Folded-in figures from the retired v10_retrofit_report.md."""
    module_counts = {fname: len(edges) for _, edges, fname in modules}
    et_counts = Counter()
    for _, edges, _ in modules:
        et_counts.update(e["edge_type"] for e in edges)
    lines = ["## Graph composition", "", "### Module inventory"]
    for n, c in module_counts.items():
        lines.append(f"- `{n}`: {c} edges")
    lines.append("")
    lines.append("### Edge-type distribution")
    for t, c in sorted(et_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- `{t}`: {c}")
    lines.append("")
    if node_labels_path.exists():
        labels = json.loads(node_labels_path.read_text())
        stubs = sum(1 for e in labels
                    if e.get("label_short_source") == "stub_pending_adjudication")
        lines.append("### Label file")
        lines.append(f"- Total label entries: {len(labels)}")
        lines.append(f"- Stub entries pending adjudication: {stubs}")
        lines.append(f"- Reviewed / adjudicated entries: {len(labels) - stubs}")
        lines.append("")
    return lines


def main():
    ap = argparse.ArgumentParser(description="Unified config-driven diagnostic audit.")
    ap.add_argument("--version", required=True)
    ap.add_argument("--config", default="pipeline_config.json")
    args = ap.parse_args()

    cfg = load_config(args.config)
    route_map = cfg["modules"]["route_map"]
    # Report file/title follow the historical V<number> convention; accept either "v12" or "12".
    report_version = args.version.lstrip("vV")
    # Whitelist entries may be a bare [A, B] pair (legacy) or {"pair": [A, B], "reason": "..."}.
    whitelist = {}
    for entry in cfg.get("name_pair_whitelist", []):
        if isinstance(entry, dict):
            whitelist[frozenset(entry["pair"])] = entry.get("reason", "")
        else:
            whitelist[frozenset(entry)] = ""

    modules, missing = load_modules(cfg["_modules_dir"], route_map)
    total_edges = sum(len(edges) for _, edges, _ in modules)
    node_modules = collect_nodes(modules)
    unique_nodes = len(node_modules)

    G = nx.Graph()
    for _, edges, _ in modules:
        for e in edges:
            G.add_edge(e["source_node"], e["target_node"])
    n_components = nx.number_connected_components(G)
    # Connectivity is a REPORTED metric (V17-INVARIANT), never a blocking gate here. Enumerate
    # islands (non-giant components) and list their members so fragmentation is visible rather
    # than a silent count.
    _components = sorted((sorted(c) for c in nx.connected_components(G)), key=len, reverse=True)
    islands = _components[1:]

    a1_lines, a1_stats = audit_1_canonical_names(node_modules, whitelist)
    a2_lines, a2_stats = audit_2_temporal(modules)
    a3_lines, a3_stats = audit_3_dedup(modules)
    a4_lines, a4_stats = audit_4_residency(modules)
    comp_lines = composition_section(modules, cfg["_node_labels"])

    next_steps = []
    if a3_stats["literal_dups"] > 0:
        next_steps.append(
            f"**BLOCKING**: {a3_stats['literal_dups']} literal-duplicate edge group(s) in Audit 3 Check A "
            "must be resolved (merge pipeline failure).")
    if a4_stats["residency_findings"] > 0:
        next_steps.append(
            f"**BLOCKING**: {a4_stats['residency_findings']} residency_at edge(s) in Audit 4 fail the "
            "[residency_at_reason: X] token gate (missing/duplicate/off-list reason).")
    if a1_stats["institution_high_ratio"] > 0:
        next_steps.append(
            f"Adjudicate {a1_stats['institution_high_ratio']} institution pair(s) with similarity ≥ 0.95 "
            "(or whitelist if confirmed distinct).")
    if a2_stats["inversions"] > 0:
        next_steps.append(f"Fix {a2_stats['inversions']} temporal inversion(s) (start_year > end_year).")
    if a2_stats["sentinels"] > 0:
        next_steps.append(f"Review {a2_stats['sentinels']} edge(s) with sentinel/out-of-range temporal values.")
    if a3_stats["multi_gov_overlap"] > 0:
        next_steps.append(
            f"Review {a3_stats['multi_gov_overlap']} overlapping governance_leadership tenure(s).")
    if not next_steps:
        next_steps.append("Zero blocking issues surfaced.")

    if missing:
        next_steps.append(f"Missing module files: {missing}")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = [
        f"# V{report_version} Diagnostic Audit",
        f"Generated: {ts}",
        f"Graph state: {total_edges} edges across {len(modules)} module files, "
        f"{unique_nodes} unique nodes, {n_components} connected component(s)"
        + ("" if not islands else
           " — islands (non-giant components): "
           + "; ".join(f"{len(i)} node(s) {i}" for i in islands)),
        "",
        "## Summary of findings",
        f"- **Audit 1 (Canonical Names):** {a1_stats['person_pairs']} person pair(s), "
        f"{a1_stats['institution_pairs']} institution pair(s), "
        f"{a1_stats['society_pairs']} society pair(s) flagged "
        f"(institution pairs ≥ 0.95: {a1_stats['institution_high_ratio']}; "
        f"whitelisted: {a1_stats['suppressed']})",
        f"- **Audit 2 (Temporal):** {a2_stats['sentinels']} sentinel/out-of-range, "
        f"{a2_stats['inversions']} logical inversion(s), "
        f"{a2_stats['same_year']} same-year ranged edge(s), "
        f"{a2_stats['round_clusters_flagged']} round-year cluster(s) flagged",
        f"- **Audit 3 (Dedup):** {a3_stats['literal_dups']} literal duplicate group(s), "
        f"{a3_stats['multi_type_pairs']} multi-type pair(s), "
        f"{a3_stats['multi_gov']} multi-governance case(s) "
        f"(overlapping: {a3_stats['multi_gov_overlap']})",
        f"- **Audit 4 (residency_at tokens):** {a4_stats['residency_edges']} residency_at edge(s) "
        f"checked, {a4_stats['residency_findings']} blocking token violation(s)",
        "",
        "## Recommended next steps",
    ]
    for step in next_steps:
        header.append(f"- {step}")
    header.append("")
    header.append("---")
    header.append("")

    out = "\n".join(
        header
        + comp_lines + ["---", ""]
        + a1_lines + ["---", ""]
        + a2_lines + ["---", ""]
        + a3_lines + ["---", ""]
        + a4_lines
    )
    report_path = cfg["_reports_dir"] / f"V{report_version}_diagnostic_audit_report.md"
    report_path.write_text(out)
    print(f"Wrote {report_path}")
    print(f"  Edges: {total_edges}  Nodes: {unique_nodes}  "
          f"Components: {n_components}  Modules loaded: {len(modules)}  "
          f"Whitelisted name pairs: {a1_stats['suppressed']}")
    if islands:
        print(f"  Islands (non-giant components, {len(islands)}) — members listed:")
        for i, isl in enumerate(islands, 1):
            print(f"    island {i} ({len(isl)} node(s)): {isl}")
    print(f"  Person name pairs flagged: {a1_stats['person_pairs']}  "
          f"| residency_at edges: {a4_stats['residency_edges']}  "
          f"blocking token violations: {a4_stats['residency_findings']}")


if __name__ == "__main__":
    main()
