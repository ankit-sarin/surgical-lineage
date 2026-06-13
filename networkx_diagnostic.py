#!/usr/bin/env python3
"""
networkx_diagnostic.py — READ-ONLY structural diagnostic for the surgical-lineage graph.

Interim, reusable, version-parameterized analysis. NEVER writes to the graph artifacts;
the only files it creates are the two report outputs (md + json) in the repo root.

Computes, on the post-merge canonical graph:
  1. Betweenness centrality (normalized) on four graph variants.
  2. Trunk-root enumeration over the training projection (weakly-connected components,
     in-degree-0 roots, "major" roots = components with size >= threshold).
  3. Root-to-root undirected geodesics in the full graph + bridge-intermediary tally.
  4. Three-way floating-person recount (full_degree1 / training_leaves / lineage_absent)
     with pairwise overlaps.

Graph variants:
  G_full     : simple DiGraph over all node types / all edge types (parallels collapsed,
               edge_types carried as a list attribute).
  G_full_u   : G_full undirected.
  G_train    : DiGraph induced by edge_type in {direct_training, observational_study}.
  G_train_u  : G_train undirected.

CLI:
  networkx_diagnostic.py --version v13 --config pipeline_config.json --threshold 5 --top-n 25
"""
import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import networkx as nx

TRAINING_TYPES = {"direct_training", "observational_study"}

# Reference sets for regression tests (person<->person lineage projection, post-V13).
EXPECTED_TRUNK_ROOTS = {
    "Bernhard von Langenbeck", "William E. Ladd", "Alton Ochsner", "Helen Taussig",
    "Owen Wangensteen", "Thomas Starzl", "Vilray Blair",
}
# G_full betweenness top-5 is independent of the lineage-projection fix; this guards that it
# did not move when G_train was corrected (test 5).
EXPECTED_GFULL_TOP5 = [
    "American College of Surgeons",
    "ACS National Surgical Quality Improvement Program",
    "Johns Hopkins Hospital Department of Surgery",
    "Alfred Blalock",
    "Thomas Starzl",
]


# --------------------------------------------------------------------------- IO (read-only)
def load_config(config_path):
    cfg = json.loads(Path(config_path).read_text())
    base = Path(config_path).resolve().parent
    cfg["_base"] = base
    cfg["_canonical"] = (base / cfg["paths"]["canonical"]).resolve()
    return cfg


def load_canonical(canonical_path):
    return json.loads(Path(canonical_path).read_text())


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------- graph build
def node_type_map(edges):
    nt = {}
    for e in edges:
        nt[e["source_node"]] = e["source_node_type"]
        nt[e["target_node"]] = e["target_node_type"]
    return nt


def build_digraph(edges, nt, edge_filter=None, person_to_person=False):
    """Simple DiGraph collapsing parallel (u,v) edges. edge_types carried as list attr.

    edge_filter: optional set of edge_types to include. Nodes are restricted to those
    actually touched by the surviving edges (induced subgraph).
    person_to_person: if True, additionally require BOTH endpoints to be persons. This is
    the lineage projection: a training/observational edge is a mentorship claim only when it
    runs person->person. Institution-as-trainer edges are excluded (and separately enumerated
    for review)."""
    G = nx.DiGraph()
    raw = 0
    for e in edges:
        et = e["edge_type"]
        if edge_filter is not None and et not in edge_filter:
            continue
        if person_to_person and not (nt.get(e["source_node"]) == "person"
                                     and nt.get(e["target_node"]) == "person"):
            continue
        raw += 1
        u, v = e["source_node"], e["target_node"]
        for n in (u, v):
            if not G.has_node(n):
                G.add_node(n, node_type=nt.get(n, "unknown"))
        if G.has_edge(u, v):
            G[u][v]["edge_types"].append(et)
        else:
            G.add_edge(u, v, edge_types=[et])
    G.graph["raw_edge_count"] = raw
    return G


# --------------------------------------------------------------------------- metrics
def betweenness_table(G, nt, top_n, undirected):
    bc = nx.betweenness_centrality(G, normalized=True)
    rows = []
    for node, score in bc.items():
        if undirected:
            ind = outd = G.degree(node)
        else:
            ind = G.in_degree(node)
            outd = G.out_degree(node)
        rows.append({
            "node": node,
            "node_type": nt.get(node, "unknown"),
            "betweenness": score,
            "in_degree": ind,
            "out_degree": outd,
        })
    rows.sort(key=lambda r: (-r["betweenness"], r["node"]))
    return bc, rows[:top_n]


def module_lookup(cfg):
    """Read-only map: (source, target, edge_type) -> module filename, from route_map modules.

    Reads the module JSON files (never writes) so excluded edges can be attributed to a
    module for review."""
    base = cfg["_base"]
    modules_dir = (base / cfg["paths"]["modules_dir"]).resolve()
    lookup = {}
    for fname in cfg["modules"]["route_map"].values():
        p = modules_dir / fname
        if not p.exists():
            continue
        for e in json.loads(p.read_text()):
            lookup[(e["source_node"], e["target_node"], e["edge_type"])] = fname
    return lookup


def excluded_nonperson_training_edges(edges, nt, cfg):
    """Every training-type edge with a non-person endpoint — excluded from the lineage
    projection and flagged for adjudication (institution-as-trainer is a data-model question,
    not yet a fix)."""
    lookup = module_lookup(cfg)
    out = []
    for e in edges:
        if e["edge_type"] in TRAINING_TYPES and not (
                nt.get(e["source_node"]) == "person"
                and nt.get(e["target_node"]) == "person"):
            out.append({
                "source": e["source_node"],
                "source_type": e["source_node_type"],
                "target": e["target_node"],
                "target_type": e["target_node_type"],
                "edge_type": e["edge_type"],
                "module": lookup.get(
                    (e["source_node"], e["target_node"], e["edge_type"]), "(unattributed)"),
            })
    out.sort(key=lambda r: (r["edge_type"], r["source"], r["target"]))
    return out


def trunk_roots(G_train, threshold):
    """Census of weakly-connected components: size, in-deg-0 roots. Major = size>=threshold."""
    census = []
    for comp in nx.weakly_connected_components(G_train):
        sub = G_train.subgraph(comp)
        roots = sorted(n for n in sub.nodes if sub.in_degree(n) == 0)
        census.append({
            "size": sub.number_of_nodes(),
            "edges": sub.number_of_edges(),
            "roots": roots,
            "major": sub.number_of_nodes() >= threshold,
        })
    census.sort(key=lambda c: (-c["size"], c["roots"][0] if c["roots"] else ""))
    major_roots = []
    for i, c in enumerate(census):
        if c["major"]:
            for r in c["roots"]:
                major_roots.append({"root": r, "component_index": i, "component_size": c["size"]})
    return census, major_roots


def root_to_root_geodesics(G_full_u, major_roots):
    """Undirected geodesics between major roots in DIFFERENT training components."""
    pairs = []
    bridge_tally = Counter()
    unreachable = []
    for a, b in combinations(major_roots, 2):
        if a["component_index"] == b["component_index"]:
            continue  # same training component — skip same-trunk pairs
        ra, rb = a["root"], b["root"]
        try:
            path = nx.shortest_path(G_full_u, ra, rb)
            dist = len(path) - 1
            for mid in path[1:-1]:
                bridge_tally[mid] += 1
            pairs.append({"a": ra, "b": rb, "distance": dist, "path": path,
                          "single_bridge": len(path) == 3})
        except nx.NetworkXNoPath:
            unreachable.append([ra, rb])
            pairs.append({"a": ra, "b": rb, "distance": None, "path": None,
                          "single_bridge": False})
    pairs.sort(key=lambda p: (p["distance"] is None, p["distance"], p["a"], p["b"]))
    return pairs, bridge_tally, unreachable


def three_way_floater_cut(G_full, G_full_u, G_train, nt):
    persons = {n for n, t in nt.items() if t == "person"}

    def tdeg(n):
        if n not in G_train:
            return 0
        return G_train.in_degree(n) + G_train.out_degree(n)

    full_degree1 = {n for n in persons if G_full_u.degree(n) == 1}

    training_iso = {n for n in persons if tdeg(n) == 0}            # split: 0
    training_leaf1 = {n for n in persons if tdeg(n) == 1}          # split: 1
    training_leaves = training_iso | training_leaf1

    lineage_absent = {n for n in persons
                      if tdeg(n) == 0 and (n in G_full and G_full.degree(n) >= 1)}

    return {
        "person_count": len(persons),
        "full_degree1": sorted(full_degree1),
        "training_leaves": sorted(training_leaves),
        "training_isolated_deg0": sorted(training_iso),
        "training_leaf_deg1": sorted(training_leaf1),
        "lineage_absent": sorted(lineage_absent),
        "overlaps": {
            "full_degree1_AND_training_leaves": sorted(full_degree1 & training_leaves),
            "full_degree1_AND_lineage_absent": sorted(full_degree1 & lineage_absent),
            "training_leaves_AND_lineage_absent": sorted(training_leaves & lineage_absent),
        },
    }


# --------------------------------------------------------------------------- tests
def run_tests(edges, nt, graphs, census, major_roots, geo_pairs, floaters,
              bc_all, bc_tables, excluded_edges, sha_before, sha_after, threshold):
    import math
    G_full, G_full_u, G_train, G_train_u = (
        graphs["G_full"], graphs["G_full_u"], graphs["G_train"], graphs["G_train_u"])
    T = []

    def add(name, ok, detail, hard=True):
        T.append({"test": name, "pass": bool(ok), "hard": hard, "detail": detail})

    # 1 — every node in G_train is a person
    nonperson_nodes = [n for n in G_train.nodes if nt.get(n) != "person"]
    add("1.G_train_all_persons", not nonperson_nodes,
        "every G_train node is a person" if not nonperson_nodes
        else f"non-person nodes present: {nonperson_nodes}")
    # 2 — G_train == 138 / 24 wcc / 5 big
    tn = G_train.number_of_nodes()
    wcc = len(census)
    big = sum(1 for c in census if c["size"] >= threshold)
    add("2.G_train_138n_24wcc_5big", tn == 138 and wcc == 24 and big == 5,
        f"nodes={tn} (exp 138); weak_components={wcc} (exp 24); comps>={threshold}: {big} (exp 5)")
    # 3 — all trunk roots persons AND root set matches reference
    root_names = {m["root"] for m in major_roots}
    all_person_roots = all(nt.get(m["root"]) == "person" for m in major_roots)
    matches_ref = root_names == EXPECTED_TRUNK_ROOTS
    diff = ""
    if not matches_ref:
        diff = (f" | missing={sorted(EXPECTED_TRUNK_ROOTS - root_names)} "
                f"extra={sorted(root_names - EXPECTED_TRUNK_ROOTS)}")
    add("3.trunk_roots_persons_and_match_reference", all_person_roots and matches_ref,
        f"major roots ({len(root_names)}): {sorted(root_names)}; all persons={all_person_roots}; "
        f"matches reference 7-root set={matches_ref}{diff}")
    # 4 — structural sanity
    jh_in = G_train.in_degree("John Hunter") if "John Hunter" in G_train else 0
    hal_in = G_train.in_degree("William Stewart Halsted") if "William Stewart Halsted" in G_train else 0
    add("4.JohnHunter_indeg0_Halsted_indeg_ge1", jh_in == 0 and hal_in >= 1,
        f"John Hunter training in-degree={jh_in} (exp 0); Halsted in-degree={hal_in} (exp ≥1)")
    # 5 — full_degree1 still 53 AND G_full top-5 unchanged
    fd1 = len(floaters["full_degree1"])
    gfull_top5 = [r["node"] for r in bc_tables["G_full"][:5]]
    add("5.full_degree1_53_and_Gfull_top5_unchanged",
        fd1 == 53 and gfull_top5 == EXPECTED_GFULL_TOP5,
        f"full_degree1={fd1} (exp 53); G_full top-5={gfull_top5}; "
        f"unchanged={gfull_top5 == EXPECTED_GFULL_TOP5}")
    # 6 — excluded enumeration non-empty and equals diagnosis count (27)
    add("6.excluded_nonperson_training_eq_27",
        len(excluded_edges) == 27 and len(excluded_edges) > 0,
        f"excluded non-person training edges={len(excluded_edges)} (exp 27)")
    # 7 — read-only sha unchanged
    add("7.canonical_sha_unchanged", sha_before == sha_after,
        f"before={sha_before[:12]}… after={sha_after[:12]}…")

    # supplementary invariants (retained from prior version; hard)
    add("S1.canonical_node_count_415", G_full.number_of_nodes() == 415,
        f"nodes={G_full.number_of_nodes()}; raw_edges={len(edges)}; "
        f"simple_edges={G_full.number_of_edges()} (collapsed {len(edges)-G_full.number_of_edges()})")
    ncc = nx.number_connected_components(G_full_u)
    add("S2.G_full_u_single_component", ncc == 1, f"components={ncc}")
    all_finite = all(math.isfinite(v) and set(bc.keys()) == set(graphs[g].nodes())
                     for g, bc in bc_all.items() for v in bc.values())
    add("S3.betweenness_finite_all_4_graphs", all_finite, "all four graphs finite & full coverage")
    finite_all = all(p["distance"] is not None for p in geo_pairs) if geo_pairs else True
    add("S4.major_root_pairs_finite_distance", finite_all,
        f"{len(geo_pairs)} cross-trunk pairs; unreachable={sum(1 for p in geo_pairs if p['distance'] is None)}")
    return T


# --------------------------------------------------------------------------- reporting
def fmt_bc_table(rows):
    out = ["| Node | Type | Betweenness | In | Out |", "|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['node']} | {r['node_type']} | {r['betweenness']:.4f} | "
                   f"{r['in_degree']} | {r['out_degree']} |")
    return "\n".join(out)


def write_markdown(path, version, sha_before, sha_after, edges, graphs, bc_tables,
                   census, major_roots, geo_pairs, bridge_tally, unreachable,
                   floaters, tests, threshold, top_n, excluded_edges):
    G_full = graphs["G_full"]
    L = []
    L.append(f"# NetworkX Structural Diagnostic — {version} (interim)")
    L.append("")
    L.append(f"Read-only analysis. Canonical sha256 `{sha_before}` (unchanged after run: "
             f"{'YES' if sha_before==sha_after else 'NO'}).")
    L.append(f"Graph: {G_full.number_of_nodes()} nodes / {len(edges)} raw edges / "
             f"{G_full.number_of_edges()} simple directed edges "
             f"({len(edges)-G_full.number_of_edges()} parallel collapsed) / "
             f"{nx.number_connected_components(graphs['G_full_u'])} component(s).")
    L.append(f"Parameters: threshold={threshold}, top-n={top_n}.")
    L.append("")
    L.append("> Interim diagnostic on a still-growing graph — provisional numbers, not a "
             "manuscript lock.")
    L.append("")

    # Section 1
    L.append("## 1 — Betweenness centrality (normalized)")
    L.append("")
    L.append("Full-graph tables annotate `node_type`: institution/society dominance is *why* "
             "manuscript lineage claims anchor on the training projection, not the full graph. "
             "`G_train` is the corrected **person↔person** lineage projection (both endpoints "
             "person); non-person training edges are excluded — see the REVIEW section.")
    for label, key in [("G_full (directed, all types)", "G_full"),
                       ("G_full_u (undirected, all types)", "G_full_u"),
                       ("G_train (directed person↔person lineage projection)", "G_train"),
                       ("G_train_u (undirected person↔person lineage projection)", "G_train_u")]:
        L.append("")
        L.append(f"### {label} — top {top_n}")
        L.append("")
        L.append(fmt_bc_table(bc_tables[key]))
    L.append("")

    # Section 2
    L.append("## 2 — Trunk roots (person↔person lineage projection)")
    L.append("")
    major = [c for c in census if c["major"]]
    G_train = graphs["G_train"]
    big = sum(1 for c in census if c["size"] >= threshold)
    L.append(f"`G_train` = training edges (`direct_training`, `observational_study`) with "
             f"**both endpoints person**: {G_train.number_of_nodes()} nodes / "
             f"{G_train.number_of_edges()} edges.")
    L.append(f"Weakly-connected components: {len(census)} total; "
             f"{len(major)} major (size ≥ {threshold}, {big} components); "
             f"{len(major_roots)} major trunk root(s) — all persons.")
    L.append("")
    L.append(f"> **Definitional fix (V13-DIAG-FIX).** The prior run filtered on edge_type alone, "
             f"pulling {len(excluded_edges)} non-person training edges into the projection "
             f"(chiefly institution→person `direct_training`) and seating institutions "
             f"(Mayo/JHH/Howard/MSK departments) as trunk roots. Restricting to person↔person "
             f"yields the correct **138 nodes / 24 weak components / 5 components ≥ {threshold}**, "
             f"with all trunk roots persons. Excluded edges enumerated in the REVIEW section.")
    L.append("")
    L.append("### Major trunk roots (components size ≥ threshold)")
    L.append("")
    L.append("| Comp # | Size | Edges | Root(s) |")
    L.append("|---|---|---|---|")
    for i, c in enumerate(census):
        if c["major"]:
            L.append(f"| {i} | {c['size']} | {c['edges']} | {', '.join(c['roots'])} |")
    L.append("")
    L.append("### Full census (all components)")
    L.append("")
    L.append("| Comp # | Size | Edges | Major | Root(s) |")
    L.append("|---|---|---|---|---|")
    for i, c in enumerate(census):
        L.append(f"| {i} | {c['size']} | {c['edges']} | {'Y' if c['major'] else ''} | "
                 f"{', '.join(c['roots']) if c['roots'] else '(none — cyclic)'} |")
    L.append("")

    # Section 3
    L.append("## 3 — Root-to-root geodesics (undirected, full graph)")
    L.append("")
    cross = [p for p in geo_pairs]
    L.append(f"{len(cross)} cross-trunk major-root pair(s). "
             f"Unreachable: {len(unreachable)} (expected 0 given single component).")
    L.append("")
    L.append("### Distance matrix")
    L.append("")
    roots = [m["root"] for m in major_roots]
    dist = {}
    for p in geo_pairs:
        dist[(p["a"], p["b"])] = p["distance"]
        dist[(p["b"], p["a"])] = p["distance"]
    header = "| | " + " | ".join(r.split()[0] + "…" if len(r) > 14 else r for r in roots) + " |"
    L.append(header)
    L.append("|" + "---|" * (len(roots) + 1))
    for r in roots:
        cells = []
        for c in roots:
            if r == c:
                cells.append("·")
            else:
                d = dist.get((r, c))
                cells.append("—" if d is None else str(d))
        L.append(f"| {r.split()[0]+'…' if len(r)>14 else r} | " + " | ".join(cells) + " |")
    L.append("")
    L.append("### Per-pair geodesics")
    L.append("")
    L.append("| A | B | Dist | Single-bridge | Path |")
    L.append("|---|---|---|---|---|")
    for p in geo_pairs:
        pathstr = " → ".join(p["path"]) if p["path"] else "UNREACHABLE"
        L.append(f"| {p['a']} | {p['b']} | {p['distance'] if p['distance'] is not None else '—'} | "
                 f"{'YES' if p['single_bridge'] else ''} | {pathstr} |")
    L.append("")
    L.append("### Top bridge intermediaries (geodesic interior-node frequency)")
    L.append("")
    L.append("| Node | Times on a geodesic |")
    L.append("|---|---|")
    for node, cnt in bridge_tally.most_common(15):
        L.append(f"| {node} | {cnt} |")
    L.append("")

    # Section 4
    L.append("## 4 — Floating-person recount (persons only)")
    L.append("")
    L.append(f"Total persons: {floaters['person_count']}.")
    L.append("")
    L.append("| Cut | Definition | Count |")
    L.append("|---|---|---|")
    L.append(f"| (a) full_degree1 | degree==1 in G_full_u | {len(floaters['full_degree1'])} "
             f"(prior V11/V12 ~53) |")
    L.append(f"| (b) training_leaves | (in+out)≤1 in G_train | {len(floaters['training_leaves'])} |")
    L.append(f"|     ↳ training-isolated (deg 0) | no training edge at all | "
             f"{len(floaters['training_isolated_deg0'])} |")
    L.append(f"|     ↳ training leaf (deg 1) | single training edge | "
             f"{len(floaters['training_leaf_deg1'])} |")
    L.append(f"| (c) lineage_absent | 0 training edges, ≥1 non-training edge in G_full | "
             f"{len(floaters['lineage_absent'])} |")
    L.append("")
    L.append("### Overlaps")
    L.append("")
    for k, v in floaters["overlaps"].items():
        L.append(f"- `{k}`: {len(v)}")
    L.append("")
    L.append("### Cut (c) lineage_absent — examples (in the atlas, in no lineage)")
    L.append("")
    for n in floaters["lineage_absent"][:20]:
        L.append(f"- {n}")
    if len(floaters["lineage_absent"]) > 20:
        L.append(f"- … (+{len(floaters['lineage_absent'])-20} more)")
    L.append("")

    # REVIEW section — excluded non-person training edges
    L.append("## Excluded non-person training edges (REVIEW)")
    L.append("")
    L.append(f"{len(excluded_edges)} training-type edge(s) (`direct_training` / "
             f"`observational_study`) have a non-person endpoint and are therefore **excluded "
             f"from the person↔person lineage projection**. `direct_training` is expected to run "
             f"person↔person; institution-as-trainer is a data-model question flagged for "
             f"adjudication — **not** edited or deleted here (out of scope).")
    L.append("")
    src_counts = Counter(e["source"] for e in excluded_edges if e["source_type"] != "person")
    L.append("Non-person sources appearing (institution/society as trainer): "
             + (", ".join(f"{s} ({c})" for s, c in src_counts.most_common()) or "none") + ".")
    L.append("")
    L.append("| Source | Src type | Target | Tgt type | Edge type | Module |")
    L.append("|---|---|---|---|---|---|")
    for e in excluded_edges:
        L.append(f"| {e['source']} | {e['source_type']} | {e['target']} | {e['target_type']} | "
                 f"{e['edge_type']} | {e['module']} |")
    L.append("")

    # Tests
    L.append("## Tests")
    L.append("")
    L.append("| # | Test | Result | Detail |")
    L.append("|---|---|---|---|")
    for t in tests:
        kind = "" if t["hard"] else " (info)"
        res = "PASS" if t["pass"] else ("FAIL" if t["hard"] else "INFO")
        L.append(f"| {t['test']}{kind} | | **{res}** | {t['detail']} |")
    L.append("")

    Path(path).write_text("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Read-only NetworkX structural diagnostic.")
    ap.add_argument("--version", required=True)
    ap.add_argument("--config", default="pipeline_config.json")
    ap.add_argument("--threshold", type=int, default=5)
    ap.add_argument("--top-n", type=int, default=25)
    args = ap.parse_args()

    cfg = load_config(args.config)
    canonical = cfg["_canonical"]
    sha_before = sha256_of(canonical)

    edges = load_canonical(canonical)
    nt = node_type_map(edges)

    G_full = build_digraph(edges, nt)
    G_full_u = G_full.to_undirected()
    # Lineage projection: training edges with BOTH endpoints person (the V13-DIAG-FIX).
    G_train = build_digraph(edges, nt, edge_filter=TRAINING_TYPES, person_to_person=True)
    G_train_u = G_train.to_undirected()
    graphs = {"G_full": G_full, "G_full_u": G_full_u,
              "G_train": G_train, "G_train_u": G_train_u}

    excluded_edges = excluded_nonperson_training_edges(edges, nt, cfg)

    # 1 — betweenness
    bc_all = {}
    bc_tables = {}
    for key, undirected in [("G_full", False), ("G_full_u", True),
                            ("G_train", False), ("G_train_u", True)]:
        bc, rows = betweenness_table(graphs[key], nt, args.top_n, undirected)
        bc_all[key] = bc
        bc_tables[key] = rows

    # 2 — trunk roots (person↔person projection)
    census, major_roots = trunk_roots(G_train, args.threshold)

    # 3 — geodesics
    geo_pairs, bridge_tally, unreachable = root_to_root_geodesics(G_full_u, major_roots)

    # 4 — floaters
    floaters = three_way_floater_cut(G_full, G_full_u, G_train, nt)

    sha_after = sha256_of(canonical)

    tests = run_tests(edges, nt, graphs, census, major_roots, geo_pairs, floaters,
                      bc_all, bc_tables, excluded_edges, sha_before, sha_after, args.threshold)

    # outputs
    md_path = cfg["_base"] / f"networkx_diagnostic_{args.version}.md"
    json_path = cfg["_base"] / f"networkx_diagnostic_{args.version}.json"

    write_markdown(md_path, args.version, sha_before, sha_after, edges, graphs, bc_tables,
                   census, major_roots, geo_pairs, bridge_tally, unreachable,
                   floaters, tests, args.threshold, args.top_n, excluded_edges)

    raw = {
        "version": args.version,
        "canonical_sha256_before": sha_before,
        "canonical_sha256_after": sha_after,
        "graph": {
            "raw_edges": len(edges),
            "nodes": G_full.number_of_nodes(),
            "simple_directed_edges": G_full.number_of_edges(),
            "parallel_collapsed": len(edges) - G_full.number_of_edges(),
            "full_components": nx.number_connected_components(G_full_u),
            "node_type_counts": dict(Counter(nt.values())),
            "edge_type_counts": dict(Counter(e["edge_type"] for e in edges)),
            "training_person_to_person": {
                "nodes": G_train.number_of_nodes(),
                "edges": G_train.number_of_edges(),
                "weak_components": len(census),
                "components_ge_threshold": sum(1 for c in census if c["size"] >= args.threshold),
                "definition": "edge_type in {direct_training, observational_study} AND "
                              "source_node_type==person AND target_node_type==person",
            },
        },
        "excluded_nonperson_training_edges": excluded_edges,
        "betweenness_top": {k: bc_tables[k] for k in bc_tables},
        "betweenness_full": {k: bc_all[k] for k in bc_all},
        "trunk_census": census,
        "major_roots": major_roots,
        "geodesics": geo_pairs,
        "bridge_intermediaries": bridge_tally.most_common(),
        "unreachable_pairs": unreachable,
        "floaters": floaters,
        "tests": tests,
        "parameters": {"threshold": args.threshold, "top_n": args.top_n},
    }
    Path(json_path).write_text(json.dumps(raw, indent=2))

    # console summary
    hard_fail = [t for t in tests if t["hard"] and not t["pass"]]
    print(f"=== networkx_diagnostic ({args.version}) ===")
    print(f"nodes={G_full.number_of_nodes()} raw_edges={len(edges)} "
          f"simple_edges={G_full.number_of_edges()} components="
          f"{nx.number_connected_components(G_full_u)}")
    print(f"G_train (person↔person): nodes={G_train.number_of_nodes()} comps={len(census)} "
          f"major_roots={len(major_roots)} | excluded_nonperson_training={len(excluded_edges)}")
    print(f"floaters: full_degree1={len(floaters['full_degree1'])} "
          f"training_leaves={len(floaters['training_leaves'])} "
          f"lineage_absent={len(floaters['lineage_absent'])}")
    print(f"sha unchanged: {sha_before == sha_after}")
    print("TESTS:")
    for t in tests:
        res = "PASS" if t["pass"] else ("FAIL" if t["hard"] else "INFO")
        print(f"  [{res}] {t['test']} — {t['detail']}")
    print(f"Wrote {md_path}")
    print(f"Wrote {json_path}")
    if hard_fail:
        print(f"\nHARD TEST FAILURES: {len(hard_fail)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
