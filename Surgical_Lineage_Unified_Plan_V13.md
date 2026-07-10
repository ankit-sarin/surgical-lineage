# Surgical Lineage Atlas — Unified Plan
## v13

**Author:** Ankit Sarin, MD
**Date:** 2026-07-04
**Status:** V13 graph merged, committed, and pushed (552 edges / 415 nodes / 1 component). Reference docs (`README.md`, `SURGICAL_LINEAGE_ATLAS.md`) refreshed to V13 figures and pushed (`origin/main` at `07c5e5f`). Graph unchanged this session — no merge. Next session: adjudicate the 27 institution-as-trainer edges the NetworkX diagnostic surfaced, then the John G. Hunter node add and V13 approximate-year pinning.

---

## 1. What This Is

A citation-backed directed knowledge graph mapping the training lineages, institutional founding chains, and professional society networks of American surgery from 1777 through the present. The project sits at the intersection of digital humanities, surgical history, and network science, with goals spanning academic publication, open dataset contribution, and surgical education. Operates under the Digital Surgeon research initiative brand.

## 2. Architecture

**Graph schema (v3):** JSON edge arrays conforming to `00_schema.json` (JSON Schema draft-07). Eight edge types: `direct_training`, `observational_study`, `institutional_founder`, `institutional_succession`, `society_founder`, `governance_leadership`, `programmatic_accreditation`, `institutional_parent`. Three node types: `person`, `institution`, `society`. Three live evidence types: `PMID`, `DOI`, `institutional_archive` (a fourth, `society_verified`, remains a pending schema addition for society-provided training records).

**Storage:** 15 module files (`01`–`14` thematic + `15_institutional_hierarchy.json` for `institutional_parent` edges), `00_schema.json`, the regenerated canonical flat file (`surgical_lineage_graph_canonical.json`), and the auxiliary `node_labels_adjudicated.json` (`label_short` display names; not regenerated into canonical).

**Visualization:** `explorer_template.html` is the durable, un-versioned design-of-record. `build_explorer.py` (`--version` flag) regenerates `surgical_lineage_atlas_v<ver>.html` from canonical + node labels. New graph version = re-run the builder; no UI rework.

**Merge & validation pipeline (config-driven, stable since V12):** `phase_i_merge.py` (route by `route:` tag in notes, pre-insert duplicate-triple check, manifest A `modify_fields` + B semantic handlers with `expected_existing` guards), `phase_g_labels.py` (label stubs), `phase_h_apply.py` (canonical regeneration + derived-delta gate), `diagnostic_audit.py` (read-only name/temporal/dedup audits) — all driven by `pipeline_config.json` (15-module route map + per-route edge-type contract, repo paths, four structural invariants, `name_pair_whitelist`). Per-run variables (expansion file, manifests, version) are CLI args, not code edits. The gate is **derived-delta + invariants**: `phase_h` computes `expected_post = pre + delta` and enforces single connected component, zero duplicate triples, zero node-type conflicts, and label==node parity. **Note (corrects a stale assumption):** `phase_i` has no additive-only mode — it requires `--manifest-a`/`--manifest-b`. Additive batches pass **empty no-op manifests** (the `v13_manifest_A.json` / `v13_manifest_B.json` pattern, mirroring `v12_B_empty`); a pure-additive batch is `--expansion` + two empty manifests, not `--expansion` alone.

**Analysis pipeline (built V13):** `networkx_diagnostic.py` — read-only, config-driven (`--version`, `--threshold`, `--top-n`); reads canonical from `pipeline_config.json`. Computes betweenness centrality, trunk-root enumeration + cross-trunk shortest-path geodesics, and a three-way floating-person recount; writes `networkx_diagnostic_v<ver>.md` + `.json`. **Lineage subgraph is person↔person:** edges with `edge_type ∈ {direct_training, observational_study}` **and** both endpoints `node_type == person`. The edge-type filter alone is insufficient — the graph contains `institution→person` training edges that otherwise pollute the lineage view (see §5). Full-graph betweenness uses all node types/edge types; geodesics run on the full undirected graph (institutions/societies legitimately appear as intermediaries; only trunk-root endpoints are persons). Treated as an *interim diagnostic on a still-growing graph, not a manuscript lock.*

**Division of labor:** claude.ai (planning chat) handles architecture, research, citation verification, JSON/expansion authoring, Claude Code prompt drafting, manuscript strategy, the unified plan, and the analysis design. Claude Code (MacBook) handles file operations, merges, canonical regeneration, the explorer rebuild, audits, analysis-script runs, and git.

**Key methodological decisions (stable):**
- Training edges restricted to documented PD/APD roles; informal mentors without structural titles excluded. **Corollary surfaced V13:** `direct_training` is expected person→person — an `institution→person` training edge is a data-model question, not a lineage edge (see §5).
- `observational_study` restricted to pre-1950 (Mouret→Dubois→Reddick grandfathered).
- `governance_leadership` directionality: person → (institution | society). Dean/VC/CEO and other general-academic-administration roles are out of scope (surgical governance only) — applied in V13 (Freischlag/Bass deanships excluded).
- Evidence tier: PMID > DOI > society_verified > institutional_archive. PMID/DOI citations are citation-mcp-verified before entering an artifact; `institutional_archive` accepted for founding/biographical/appointment facts.
- Canonical naming: one root per real-world institution; sub-unit `<Root Name> <Descriptor>`, root must exactly prefix every child ID. Short labels live in `node_labels_adjudicated.json`.
- `institutional_parent` start_year = sub-unit founding year (not a chair-tenure or earliest-PMID proxy); end_year 2026 + `temporal_range: "<start>-ongoing"` for active relationships.

## 3. Current State

| Metric | V13 (committed) |
|--------|----------------:|
| Total edges | 552 |
| Total nodes | 415 |
| Connected components | 1 |
| Node types | person 212 / institution 147 / society 56 |
| Schema version | v3 (8 edge types) |
| Current explorer | `surgical_lineage_atlas_v13.html` (renders 552/415) |
| Structural audit | `V13_diagnostic_audit_report.md` (name/temporal/dedup; 0 blocking) |
| Analysis | `networkx_diagnostic_v13.md` + `.json` (betweenness / trunk-roots / floaters) |

**Edge-type distribution:** governance_leadership 158, direct_training 135, institutional_founder 98, society_founder 62, institutional_parent 46, programmatic_accreditation 24, institutional_succession 18, observational_study 11.

**Module inventory (edges):** 01:15, 02:129, 03:32, 04:44, 05:12, 06:12, 07:20, 08:75, 09:21, 10:23, 11:15, 12:89, 13:5, 14:14, 15:46.

**Evidence-type distribution:** PMID 297 (53.8%), institutional_archive 243 (44.0%), DOI 12 (2.2%).

**Labels:** 415 entries (matches node count), 327 reviewed/adjudicated, 88 stubs pending.

**Floating-person census (NetworkX diagnostic, post-V13, person nodes of 212):** full-graph degree-1 = **53** (matches V11/V12 baseline — the cleanest expansion targets); training-subgraph leaves = 170 (74 with no person→person training edge + 96 single-edge leaves); `lineage_absent` = 74 (in the atlas via governance/founder edges but in no person→person lineage — includes the V13 women-leadership additions entering via governance, as expected).

**Diagnostic headline (provisional — graph still growing):** In the person-lineage projection the top bridges are **Halsted, Cushing, Gross, Homans, Billroth** (institutions absent, as intended). The full graph is institution/society-dominated (ACS, ACS NSQIP, Johns Hopkins Dept of Surgery), which is the explicit reason lineage claims anchor on the projection. Five independent training trunks (≥5 nodes), rooted at: **Langenbeck/Ladd (35), Ochsner/Taussig (29), Wangensteen (10), Starzl (10), Blair (5)** — note Halsted is *not* a root (he descends from the German school), seating him as a mid-tree bridge rather than an origin. Across the 19 cross-trunk root pairs (0 unreachable), the trunks are stitched together predominantly through the Hopkins ecosystem: top intermediaries are **Johns Hopkins Dept of Surgery (8), Halsted (7), Billroth (5), Blalock (5), ACS (5)** — institution narrowly leads, with Halsted/Billroth the top human bridges.

**Repo:** clean on `origin/main` at `07c5e5f` (reference-doc V13 refresh; `c3cd5c4..07c5e5f`). The graph itself is unchanged since the V13 merge (`4573e07`) + NetworkX diagnostic (`c3cd5c4`); canonical sha256 `b4e141be…a795ba` untouched this session (docs-only edits). Pre-edit doc backup at `backups/refdoc_refresh_20260705T053558Z/`.

**Collaborator group:**

| Person | Institution | Role | Active Task |
|--------|------------|------|-------------|
| Ankit Sarin | UC Davis | PI, graph architect | 27-edge adjudication, John G. Hunter add, manuscript |
| Adnan Alseidi | UCSF | ACS board liaison, HPB connections | ACS dissemination positioning |
| Talar Tatarian | Jefferson | FC data lead | FC data request letter |
| Nova Szoka | WVU | MIS/fellowship hypothesis | MIS lineage conceptual framework |

## 4. What Changed This Session

- **Reference-doc figure refresh (docs-only, no graph change).** Brought `README.md` and `SURGICAL_LINEAGE_ATLAS.md` from stale figures (382/318 and 480/371 respectively) to V13 (552/415), sourced from canonical and cross-checked PASS against `V13_diagnostic_audit_report.md`. Refreshed: header/overview totals, node-type split (212/147/56), all 8 edge-type counts, 15-module tallies (incl. a newly-added `15_institutional_hierarchy` row that was absent from the README module table), and evidence-type counts (PMID 297 / DOI 12 / archive 243, now exact rather than approximate). Committed + pushed at `07c5e5f` (+46/−44, two files).
- **Method: guarded compute-and-patch, not regeneration.** Every stale figure replaced under an assert-then-replace guard (old value must be present first); zero guard failures across three addenda. Hand-authored prose preserved verbatim — scope/thematic descriptions, "key figures" columns, schema-v3 semantics, the Task-2B section, and all dated changelog/provenance/verification tables were left untouched by design (canonical yields totals and distributions, not narrative).
- **394-edge figure anchored, not changed.** The present-tense "contains all 394 edges" line sits inside the frozen 2026-03-15 consolidation narrative (14 modules, retired `reorganize_graph.py`, `consolidated/`). Refreshing the number in isolation would have made it inconsistent with its own paragraph, so it was anchored — "(as of the 2026-03-15 consolidation)" — to read as historical rather than as a stale live count.
- **Project instructions block authored** (standalone, 9 sections) for the claude.ai project instructions field: orientation, authority hierarchy (read the Plan live, never hardcode counts), scope bar, citation discipline, lineage predicate, division of labor (default implementer = Claude Code on MacBook), workflow loop, publishing, and society partnerships. Durable invariants only; all moving figures/rosters/rankings deferred to this Plan.

## 5. Open Issues & Blockers

1. **27 institution-as-trainer edges (data-model adjudication).** 23 `direct_training` + 4 `observational_study` with a non-person (mostly institution) source — Johns Hopkins Dept of Surgery sources 9. They falsely anchored ~16 persons into the lineage. Each needs adjudication: re-attribute to the era's named PD/chair (converts to real person→person lineage) or, if genuinely mentorless, flag for a schema decision (no "residency-at" edge type exists). Full table in `networkx_diagnostic_v13.md`.
2. **John G. Hunter node add.** The existing "John Hunter" node is confirmed clean — the 18th-c. anatomist (edges only to Physick 1788 and Cline 1777), *not* modern MIS surgeon John G. Hunter, who is simply absent. Add J.G. Hunter as a distinct node (module 11) when convenient; not a blocker.
3. **V13 approximate years.** ~13 moderate-confidence tenure/presidency start years flagged in-notes (Coselli ×2, Frazier→THI, DeBakey→Frazier span, Creech→ASA, Farmer→APSA, Bass→ABS, Bulger→UW, Donahoe→MGH span, Braunwald→UCSD span, Freischlag→SVS, Colson ×2) plus **one low-confidence placeholder** — the Houston Methodist Dept of Surgery founding year (`2004`, not a documented founding date). Pin from society past-president rosters and institutional appointment records before manuscript use.
4. **Label backlog** — 88 stubs `reviewed: false` (76 prior + 12 V13).
5. **`society_verified` schema addition + Fellowship Council data request letter** (Talar) — FC proof-of-concept blocker.
6. **Canonical `module` field is incomplete** — covers only 320/552 edges (232 unattributed). Confirm whether `build_explorer.py` or any module-based analysis reads this field before trusting it; module *files* remain authoritative for per-module tallies. Deferred, non-blocking.
7. **Data-dictionary §7/§8 describe a retired pipeline** — the "original consolidation" narrative (14 modules, `reorganize_graph.py`, `consolidated/`, "How to Expand" flow) is present-tense but superseded. Worth a dedicated prose pass to relabel as "original build (historical)"; larger than a figure refresh, deferred to a docs-modernization task.

## 6. Next Steps

1. **Adjudicate + re-attribute the 27 institution-as-trainer edges** (highest measured value). Draft the review in claude.ai: enumerate each with a proposed named-PD re-attribution where the era's chair/PD is identifiable, as a `reclassify` / `reverse_retarget` / `modify_fields` manifest; flag the genuinely mentorless ones for a schema decision. Re-attribution pulls currently-`lineage_absent` trainees into the trunks and may reshape components. This is the intended **V14** batch.
2. **Add John G. Hunter** as a distinct node (module 11 MIS), with verified training/governance edges.
3. **Pin the V13 approximate years** (and the Houston Methodist founding placeholder) from rosters/appointment records; upgrade confidence and `start_year` in a small `modify_fields` manifest.
4. **Cheap follow-ons** — `Cox→WashU Dept of Surgery`, `Schwartz→WashU Neurosurgery`, `Sutherland→University of Minnesota Transplant Program` (targets already exist; near-zero node cost).
5. **More category women** — Esserman (UCSF breast center director) and a fuller pass of the American-women-surgeons category against the governance bar.
6. **Re-run the NetworkX diagnostic** after the 27-edge re-attribution to confirm the trunk reshaping and updated bridge figures.

## 7. Publishing & Dissemination Path

**Manuscript:** Knowledge-graph structural analysis (not a history paper). Core contributions: betweenness centrality identifying non-obvious bridge figures; shortest-path analysis between independent trunk roots; the complete census of American surgical subspecialty society-to-board spawning events; the institutional-hierarchy layer enabling multi-tier traversal. *The V13 diagnostic produced provisional support for the core claims* — a measurable five-trunk structure, Halsted/Cushing/Gross as lineage bridges, and the Hopkins ecosystem (Johns Hopkins Dept + Halsted + Billroth) as the dominant cross-trunk stitching. Numbers are diagnostic, not final; the graph will expand (and the 27-edge re-attribution will shift the lineage) before submission.

**Target journals (ranked):** 1) *Journal of Surgical Education* (Elsevier, Q1) — primary, UC OA covered; 2) *Surgery* (Elsevier) — higher-impact backup, UC OA covered; 3) *Medical Teacher* (Taylor & Francis) — cost-advantaged, UC OA covered.

**Dissemination:** ACS Clinical Congress (Adnan to time), SAGES (MIS fit), interactive explorer as supplementary material or standalone resource.

## 8. Workflow Convention

**Planning (claude.ai):** architecture, research, citation verification, expansion specs, Claude Code prompts, manuscript strategy, analysis design, unified plan. **Execution (Claude Code, MacBook):** file ops, merges, canonical regeneration, explorer rebuild, audits, analysis-script runs, git.

**The core loop:** this chat produces a route-tagged expansion file (`route:` in each edge's notes) plus, when needed, match/replace manifests for edits to existing edges (`modify_fields` / `delete` / `reverse_retarget` / `reclassify`, each with `expected_existing` guards). PMID/DOI citations are citation-mcp-verified before authoring; `institutional_archive` for founding/biographical/appointment facts. Files drop into the MacBook `2026 Surgical lineage` folder; Claude Code backs up touched modules, runs the config-driven pipeline (per-run args, no new scripts), regenerates canonical, audits, and reports back. **Additive batches pass empty no-op manifests** (no additive-only mode in `phase_i`). Analysis runs (NetworkX) are **read-only** on the graph. Low-blast-radius file/Python tasks run `--dangerously-skip-permissions`; git/systemd/system config never do. Git: straight to `main`, push (no branches).

**Iterative process:** Outline → web/PubMed search (offered) → confirm → expand → refine. One batch at a time, explicit approval gates, mandatory contrarian/scope review before authoring.

## 9. Execution Pipeline (config-driven, on MacBook)

| Component | Role |
|-----------|------|
| `pipeline_config.json` | Static: 15-module route map + per-route edge-type contract, repo paths, 4 invariants, `name_pair_whitelist`. |
| `phase_i_merge.py` | Merge — route by `route:` tag, duplicate-triple check, manifest A/B guarded handlers (requires both manifest args; empty for additive). Emits `merge_run_<version>.json`. |
| `phase_g_labels.py` | Label-stub generation for new nodes. |
| `phase_h_apply.py` | Canonical regen + derived-delta gate (`expected_post = pre + delta`) + 4 invariants. |
| `diagnostic_audit.py` | Read-only name/temporal/dedup audits; writes `V<version>_diagnostic_audit_report.md`. |
| `build_explorer.py` | `--version`-aware explorer builder from `explorer_template.html` + canonical + labels. |
| `networkx_diagnostic.py` | Read-only structural analysis (betweenness, trunk-roots + geodesics, floater recount); writes `networkx_diagnostic_v<version>.md` + `.json`. Lineage subgraph = person↔person. |

**Merge invocation (no new scripts, no baseline edits):**
`phase_i_merge.py --expansion <batch>.json --manifest-a <A|empty>.json --manifest-b <B|empty>.json --version v<N> --config pipeline_config.json` → `phase_g_labels.py --config …` → `phase_h_apply.py --version v<N> --run-record merge_run_v<N>.json --config …` → `diagnostic_audit.py --version v<N> --config …` → `build_explorer.py --version v<N>`.

**Analysis invocation (read-only):** `networkx_diagnostic.py --version v<N> --config pipeline_config.json [--threshold 5 --top-n 25]`.

Archived (`archive/`, flat): spent per-version pipeline scripts and batch inputs (incl. V13 expansion + no-op manifests). `backups/` holds per-merge rollback snapshots.
