# Surgical Lineage Atlas — Unified Plan
## v15

**Author:** Ankit Sarin, MD
**Date:** 2026-07-11
**Status:** V15 merged, committed, and pushed (561 edges / 428 nodes / 1 component). Two data batches — V15-B1 (institution-as-trainer re-attribution) and V15-B2 (Bucket-C cleanup) — plus the NetworkX diagnostic re-run and a pipeline-hardening fix to `phase_g_labels.py`. `origin/main` at `be88c79`; canonical sha256 `d13d038d…3825eae`. The diagnostic confirms the lineage backbone consolidated from five trunks to one 80-node super-trunk plus three satellites. Next session: MASH→Rich re-attribution, then the `residency_at` schema PR + Batch 3.

---

## 1. What This Is

A citation-backed directed knowledge graph mapping the training lineages, institutional founding chains, and professional society networks of American surgery from 1777 through the present. The project sits at the intersection of digital humanities, surgical history, and network science, with goals spanning academic publication, open dataset contribution, and surgical education. Operates under the Digital Surgeon research initiative brand.

## 2. Architecture

**Graph schema (v3):** JSON edge arrays conforming to `00_schema.json` (JSON Schema draft-07). Eight edge types: `direct_training`, `observational_study`, `institutional_founder`, `institutional_succession`, `society_founder`, `governance_leadership`, `programmatic_accreditation`, `institutional_parent`. Three node types: `person`, `institution`, `society`. Three live evidence types: `PMID`, `DOI`, `institutional_archive`. Two schema additions remain pending: `society_verified` (society-provided training records) and `residency_at` (a person→institution training fallback for genuinely mentorless / pre-PD-era / director-unidentified cases; PR drafted this session — see §5).

**Storage:** 15 module files (`01`–`14` thematic + `15_institutional_hierarchy.json` for `institutional_parent` edges), `00_schema.json`, the regenerated canonical flat file (`surgical_lineage_graph_canonical.json`), and the auxiliary `node_labels_adjudicated.json` (`label_short` display names; not regenerated into canonical).

**Visualization:** `explorer_template.html` is the durable, un-versioned design-of-record. `build_explorer.py` (`--version` flag) regenerates `surgical_lineage_atlas_v<ver>.html` from canonical + node labels. New graph version = re-run the builder; no UI rework.

**Merge & validation pipeline (config-driven, stable since V12):** `phase_i_merge.py` (route by `route:` tag in notes, pre-insert duplicate-triple check, manifest A `modify_fields` + B semantic handlers — `delete`/`reverse_retarget`/`reclassify` — with `expected_existing` guards), `phase_g_labels.py`, `phase_h_apply.py` (canonical regeneration + derived-delta gate), `diagnostic_audit.py` (read-only name/temporal/dedup audits) — all driven by `pipeline_config.json` (15-module route map + per-route edge-type contract, repo paths, four structural invariants, `name_pair_whitelist`). Per-run variables (expansion file, manifests, version) are CLI args, not code edits. The gate is **derived-delta + invariants**: `phase_h` computes `expected_post = pre + delta` and enforces single connected component, zero duplicate triples, zero node-type conflicts, and label==node parity. `phase_i` has no additive-only mode — additive batches pass **empty no-op manifests** (manifest B type `edge_semantic_ops` with empty `operations`; manifest A type `edge_modify_fields`).

**`phase_g_labels.py` — reconcile, not append-only (hardened V15):** now performs a one-pass reconcile of the label set against the canonical node set — **appends** a stub for every new node (preserved behavior) **and prunes** every label whose node is no longer canonical (new). Every append and prune is printed by name before the terminal parity assert; a `--max-prune` guard (default 10) aborts with an itemized list rather than execute an unexpectedly large prune. This closes the gap where delete batches failed the parity assert and forced a manual label-file edit (the V15-B2 workaround). A per-id snapshot check proves every retained entry is byte-identical (allows removal, forbids silent mutation).

**Analysis pipeline (built V13):** `networkx_diagnostic.py` — read-only, config-driven (`--version`, `--threshold`, `--top-n`); reads canonical from `pipeline_config.json`. Computes betweenness centrality, trunk-root enumeration + cross-trunk shortest-path geodesics, and a three-way floating-person recount; writes `networkx_diagnostic_v<ver>.md` + `.json`. **Lineage subgraph is person↔person:** edges with `edge_type ∈ {direct_training, observational_study}` **and** both endpoints `node_type == person`. The edge-type filter alone is insufficient — the graph contains `institution→person` training edges that otherwise pollute the lineage view (the V13 27-edge REVIEW set, resolved in V15). Full-graph betweenness uses all node types/edge types; geodesics run on the full undirected graph (institutions/societies legitimately appear as intermediaries; only trunk-root endpoints are persons). Treated as an *interim diagnostic on a still-growing graph, not a manuscript lock.* **Caveat:** the script's self-tests assert against stale V13 snapshot constants and now print spurious "HARD TEST FAILURES" (the intended version-over-version deltas, not defects); the integrity invariants all pass. A hardening task to split invariants from snapshot counts is queued (§6).

**Division of labor:** claude.ai (planning chat) handles architecture, research, citation verification, JSON/expansion authoring, Claude Code prompt drafting, manuscript strategy, the unified plan, and the analysis design. Claude Code (MacBook) handles file operations, merges, canonical regeneration, the explorer rebuild, audits, analysis-script runs, and git.

**Key methodological decisions (stable):**
- Training edges restricted to documented PD/APD roles; informal mentors without structural titles excluded. **Corollary:** `direct_training` is expected person→person — an `institution→person` training edge is a data-model question, not a lineage edge (§5). **V15 ruling:** pre-1950 MD-degree edges (medical-school attendance, not residency) reclassify to `observational_study` with a documented named teacher, or hold if no teacher is documented.
- `observational_study` restricted to pre-1950 (Mouret→Dubois→Reddick grandfathered).
- `governance_leadership` directionality: person → (institution | society). Dean/VC/CEO and other general-academic-administration roles are out of scope (surgical governance only).
- Evidence tier: PMID > DOI > society_verified > institutional_archive. PMID/DOI citations are citation-mcp-verified (content-match) before entering an artifact; `institutional_archive` accepted for founding/biographical/appointment facts. **V15 lesson:** content-match is not optional — PMID 18481473 existed and named Leffall but documented his *chairmanship*, not his training; existence checks alone would have kept a mismatched citation.
- Canonical naming: one root per real-world institution; sub-unit `<Root Name> <Descriptor>`, root must exactly prefix every child ID. Short labels live in `node_labels_adjudicated.json`.
- `institutional_parent` start_year = sub-unit founding year (not a chair-tenure or earliest-PMID proxy); end_year 2026 + `temporal_range: "<start>-ongoing"` for active relationships.
- **Delete-batch discipline (V15):** deletes can orphan nodes or split the graph. Every proposed delete is connectivity-dry-run before authoring; an edge that is a node's sole tie to the tree is not a plain delete — it is either an orphan-node cleanup (if the far side is out of scope) or a re-attribution (if the far side is a legitimate figure).

## 3. Current State

| Metric | V15 (committed) |
|--------|----------------:|
| Total edges | 561 |
| Total nodes | 428 |
| Connected components | 1 |
| Node types | person 223 / institution 149 / society 56 |
| Schema version | v3 (8 edge types) |
| Current explorer | `surgical_lineage_atlas_v15_b2.html` (rebuilt at B2, renders 561/428) |
| Structural audit | `V15-B2_diagnostic_audit_report` (0 blocking; temporal 0 flags) |
| Analysis | `networkx_diagnostic_v15.md` + `.json` (untracked — pending commit, §5) |

**Edge-type distribution:** governance_leadership 164, direct_training 136, institutional_founder 98, society_founder 62, institutional_parent 49, programmatic_accreditation 24, institutional_succession 18, observational_study 10.

**Module inventory (edges):** 01:16, 02:136, 03:32, 04:44, 05:12, 06:12, 07:20, 08:75, 09:21, 10:21, 11:15, 12:89, 13:5, 14:14, 15:49.

**Evidence-type distribution:** PMID 296 (52.8%), institutional_archive 254 (45.3%), DOI 11 (2.0%).

**Labels:** 428 entries (parity holds; `phase_g` reconcile confirmed a clean no-op post-B2). Backlog ~100 stubs `reviewed: false` (94 prior + 6 new V15 person stubs: Humphreys, Goodwin, McClellan, Syphax, Child, Bell); Wennberg + Dartmouth Institute label entries pruned in B2.

**Diagnostic headline (V15, `networkx_diagnostic_v15`):** The person-lineage projection (152 person-nodes, 134 edges, 23 weak components) now has **four major trunks (≥5): an 80-node super-trunk** (in-degree-0 roots Ochsner, Langenbeck, Zuidema, Taussig, Ladd), **William J. Mayo (12), Edward P. Richardson (5), Vilray Blair (5)** — replacing V13's fragmented five-trunk 35/29/10/10/5. The consolidation is the direct effect of V15-B1: seating Starzl under Blalock and Wangensteen under W.J. Mayo dissolved two former independent roots. **Betweenness (full graph)** stays institution/society-dominated at the top (ACS 0.453, ASA 0.206, then Halsted 0.166 at #3); the standout human result is **Alfred Blalock #16→#4** (bc 0.061→0.158) and **Barney Brooks #249→#21** (~20×), confirming the corrected **Halsted→Brooks→Blalock** grand-pupil path is now load-bearing for person-to-person lineage traffic. Cross-root geodesics: 18 pairs, 0 unreachable, mean ≈5.9, max 8, stitched mainly through Edward Churchill, ABMS, the plastic-surgery boards, ACS/ABS, and MGH/Mayo departments. Name-collision watch clean: John Hunter (18c) bc 0.0047, in-degree 0 (not a bridge); John G. Hunter still absent.

**Repo:** clean on `origin/main` at `be88c79` ("phase_g_labels: add loud prune path + mass-prune guard"). This session's commit chain: `a30735f` (V15-B1) → `d7cf876` (V15-B2: Bucket-C cleanup, 561e/428n/1c) → `be88c79` (phaseg hardening). Canonical sha256 `d13d038d8c3d3541a67fcad5d2533e5e863a8ecec5d6c7eadaadf87a43825eae` (set at B2; unchanged by the read-only diagnostic and the code-only phaseg commit). V15 inputs archived to `archive/v15_*.json` and `archive/v15_batch2_*.json`; rollback snapshots under `backups/`. `name_pair_whitelist` unchanged (1 entry). *Minor:* the V14 commit label reconciliation is still loose (pre-flight found HEAD at `97a6b83`, a docs-only commit, where the `c1e016a` V14 merge was expected) — confirm `97a6b83` is a descendant of `c1e016a`, not a divergence, at the next docs pass; the canonical SHA matched the V14 lock throughout, so graph state was never in question.

**Collaborator group:**

| Person | Institution | Role | Active Task |
|--------|------------|------|-------------|
| Ankit Sarin | UC Davis | PI, graph architect | MASH→Rich re-attribution, residency_at Batch 3, manuscript |
| Adnan Alseidi | UCSF | ACS board liaison, HPB connections | ACS dissemination positioning |
| Talar Tatarian | Jefferson | FC data lead | FC data request letter |
| Nova Szoka | WVU | MIS/fellowship hypothesis | MIS lineage conceptual framework |

## 4. What Changed This Session

- **V15-B1 — institution-as-trainer re-attribution merged (562→565 edges, 424→430 nodes, 1 component).** 13 edges: 10 `reverse_retarget` (Reemtsma→Humphreys, Starzl→Blalock, Kirk→Sabiston, Walsh→Goodwin, Brennan→Moore, Wangensteen→W.J. Mayo +year-fix, Silen→Bell, Leffall→Syphax +citation-swap +year-trim, Thompson→Child, Cameron→Zuidema), 1 `reclassify` (Gross → observational_study under McClellan), 1 `delete` + 3 additive person→person edges. Six new person nodes (Humphreys, Goodwin, McClellan, Syphax, Child, Bell). Every re-attribution content-match-verified before authoring; the whole batch dry-run against the live modules (all 12 guards matched, single component held) before handoff.
- **Blalock false-lineage correction (the highest-value edit).** The `JHH→Blalock direct_training` edge asserted a Halstedian training that never happened — Blalock was *denied* the Halsted residency and trained under Barney Brooks at Vanderbilt from 1925. Deleted the false edge; authored `Barney Brooks→Blalock`, which — since `Halsted→Barney Brooks` already exists — seats Blalock correctly as Halsted's *grand*-pupil. Confirmed downstream: Blalock rose to the #4 betweenness node graph-wide.
- **Two two-edge splits.** Cameron → `Blalock` (1962–64, internship/early residency) + `Zuidema` (1964–71, bulk of residency). Thompson → `Coller` (1956–58) + `Child` (1959–64, chair from 1959). Both by documented chief tenure.
- **MD-degree ruling applied.** Gross reclassified `direct_training → observational_study` under his documented private preceptor George McClellan (PMID 16809223 content-match). Jackson and Flint held (no documented named teacher).
- **V15-B2 — Bucket-C cleanup merged (565→561 edges, 430→428 nodes, 1 component).** Re-scoped after a connectivity dry-run revealed the naive 4-delete plan would split the graph 1→3. Final: two clean deletes (`Harkins→JHH` faculty-appointment miscode; `St.Mark's→ASCRS` redundant institution↔society tie) + one delete-with-orphan-cleanup (`Flum→Dartmouth` plus `Wennberg→Dartmouth`, removing two out-of-scope health-policy nodes). **`MASH→Rich` pulled entirely** — deleting it would orphan a legitimate surgeon; routed to the re-attribution queue instead.
- **V15-DIAG — NetworkX re-run (read-only).** Confirmed the 80/12/5/5 trunk census exactly as forecast and the Blalock/Brooks bridge lift. Wrote `networkx_diagnostic_v15.{md,json}` (left untracked for review).
- **V15-PHASEG-PRUNE — pipeline hardening (code-only).** Added the loud prune path + mass-prune guard to `phase_g_labels.py`; 9/9 pytest, live no-op on the reconciled 428 graph. Committed independently (`be88c79`).
- **`residency_at` schema PR drafted** (`residency_at_schema_PR.md`) for Batch 3 — not landed.

## 5. Open Issues & Blockers

1. **`MASH→Rich` re-attribution (next batch).** Norman Rich's only tie to the tree was the miscoded `MASH→Rich observational_study`; he is a legitimate surgeon (Vietnam Vascular Registry founder), so deletion was declined. Needs his real Walter Reed / DeBakey-line PD researched and verified, then a `reverse_retarget` to a named trainer (preserving Rich + VVR's connection).
2. **`residency_at` schema PR + Batch 3.** PR drafted (add 9th edge type, person→institution, projection-excluded by construction). After it lands, convert the genuinely mentorless holds: `Coller→MGH` (mentorless-by-committee, PMID 14036574), `Clark→Mayo` (pre-PD-era), `Leffall→MSK` (director-unidentified; **needs a non-defective citation**), and the `Mathews`/St. Mark's judgment call. The V15 diagnostic re-confirmed exactly **12 excluded institution-sourced training edges** — the Batch-3 surface.
3. **The V15 hold set (needs nodes or scope rulings).** Hart, Blakemore, Flint, Jackson, Safar, Firor — the post-Halsted JHH interregnum cohort + MD-degree cases + the anesthesiology-scope question. Most need an interim-Hopkins-leadership node (Dean Lewis) or a documented named teacher before re-attribution.
4. **`networkx_diagnostic_v15.{md,json}` untracked.** Recommend a clean standalone commit to preserve the provenance chain (the V13 reports are tracked; the plan increment cites these figures).
5. **`networkx_diagnostic.py` stale self-tests (hardening, no urgency).** The 5 "HARD TEST FAILURES" are V13 snapshot constants (415 nodes, 138 projection nodes, etc.) that legitimately change each version; split true invariants (keep as asserts) from version-snapshot counts (make informational). Code-only; slot before manuscript prep. `TASK V15-DIAG-BASELINE` ready to spec on request.
6. **Known-collision watchlist (disambiguate-at-add-time).** `John Hunter` (18c, in-graph) vs `John G. Hunter` (modern MIS, absent — add distinct, module 11). `Larry H. Hollier` Sr. (in-graph) vs Jr. (absent — distinct ID if added).
7. **Reference docs + V14 commit reconciliation.** `README.md` and `SURGICAL_LINEAGE_ATLAS.md` are now two versions stale (last at V13/552); refresh to V15 in the next docs pass, and confirm the `97a6b83`/`c1e016a` lineage at the same time. `society_verified` schema + Fellowship Council letter (Talar) remain the FC proof-of-concept blocker. Canonical `module` field still partial (module files authoritative); data-dictionary §7/§8 still describe the retired pipeline. All non-blocking.

## 6. Next Steps

1. **`MASH→Rich` re-attribution** — research Rich's documented PD (Walter Reed / DeBakey line), verify with citation-mcp, author a `reverse_retarget` manifest, dry-run connectivity, merge.
2. **`residency_at` schema PR** — land the 9th edge type (schema + `networkx_diagnostic` docstring note), then author **Batch 3** converting the 4 mentorless holds (secure a training-specific citation for Leffall→MSK; decide the Mathews judgment call).
3. **Commit the V15 diagnostic reports** (`networkx_diagnostic_v15.{md,json}`) — standalone git commit, no graph change.
4. **`TASK V15-DIAG-BASELINE`** — split the diagnostic's invariant asserts from version-snapshot counts so "HARD TEST FAILURES" stops misleading; before manuscript prep, not before the next data batch.
5. **Work the hold set** — add the interim-Hopkins-leadership node(s) (Dean Lewis) to enable Hart/Blakemore re-attribution; resolve the MD-degree and anesthesiology-scope holds.
6. **Mount Sinai follow-on** (carried) — Garlock + Kark once tenure dates are archive-pinned; optional Hollier→Mayo Vascular Division; set the RMTI `label_short`. **Cheap follow-ons:** `Cox→WashU Dept of Surgery`, `Schwartz→WashU Neurosurgery`, `Sutherland→Univ Minnesota Transplant Program`.
7. **Refresh `README.md` + `SURGICAL_LINEAGE_ATLAS.md` to V15** and reconcile the V14 commit label (docs-only).

## 7. Publishing & Dissemination Path

**Manuscript:** Knowledge-graph structural analysis (not a history paper). Core contributions: betweenness centrality identifying non-obvious bridge figures; shortest-path analysis between independent trunk roots; the complete census of American surgical subspecialty society-to-board spawning events; the institutional-hierarchy layer enabling multi-tier traversal. **The V15 diagnostic sharpened the central structural story:** correctly resolving institution-sourced training edges to their human PDs consolidates the lineage into a single dominant 80-node trunk (from V13's fragmented five), and surfaces the Halsted→Brooks→Blalock grand-pupil path as a top-5 betweenness bridge — a concrete, non-obvious result the framing is built to deliver. The persistence of institutions/societies (ACS/ASA/boards) at the very top of full-graph betweenness is itself a methods point: it justifies anchoring lineage claims on the person-only projection. Numbers remain interim; the graph will expand (MASH→Rich, Batch 3, the hold set) before submission.

**Target journals (ranked):** 1) *Journal of Surgical Education* (Elsevier, Q1) — primary, UC OA covered; 2) *Surgery* (Elsevier) — higher-impact backup, UC OA covered; 3) *Medical Teacher* (Taylor & Francis) — cost-advantaged, UC OA covered.

**Dissemination:** ACS Clinical Congress (Adnan to time), SAGES (MIS fit), interactive explorer as supplementary material or standalone resource.

## 8. Workflow Convention

**Planning (claude.ai):** architecture, research, citation verification, expansion specs, Claude Code prompts, manuscript strategy, analysis design, unified plan. **Execution (Claude Code, MacBook):** file ops, merges, canonical regeneration, explorer rebuild, audits, analysis-script runs, git.

**The core loop:** this chat produces a route-tagged expansion file (`route:` in each edge's notes) plus, when needed, match/replace manifests for edits to existing edges (`modify_fields` / `delete` / `reverse_retarget` / `reclassify`, each with `expected_existing` guards). PMID/DOI citations are citation-mcp-verified (content-match, not existence) before authoring; `institutional_archive` for founding/biographical/appointment facts. Files drop into the MacBook `2026 Surgical lineage` folder; Claude Code backs up touched modules, runs the config-driven pipeline (per-run args, no new scripts), regenerates canonical, audits, and reports back. **Additive batches pass empty no-op manifests.** **Every batch — especially deletes — is connectivity-dry-run in the planning chat before handoff; single component is validated, not assumed.** Analysis runs (NetworkX) are **read-only** on the graph. Low-blast-radius file/Python tasks run `--dangerously-skip-permissions`; git/systemd/system config never do. Git: straight to `main`, push (no branches).

**Iterative process:** Outline → web/PubMed search (offered) → confirm → expand → refine. One batch at a time, explicit approval gates, mandatory contrarian/scope review before authoring. The architect owns spec errors: hold the commit, issue a corrective spec, re-run, then commit (the V15-B2 re-scope is the canonical example — the connectivity dry-run caught a 3-way split before handoff).

## 9. Execution Pipeline (config-driven, on MacBook)

| Component | Role |
|-----------|------|
| `pipeline_config.json` | Static: 15-module route map + per-route edge-type contract, repo paths, 4 invariants, `name_pair_whitelist`. |
| `phase_i_merge.py` | Merge — route by `route:` tag, duplicate-triple check, manifest A/B guarded handlers (requires both manifest args; empty for additive). Emits `merge_run_<version>.json`. |
| `phase_g_labels.py` | Label reconcile — **append** stubs for new nodes **+ prune** labels for removed nodes (loud, itemized, `--max-prune` guard, per-id byte-stability check). |
| `phase_h_apply.py` | Canonical regen + derived-delta gate (`expected_post = pre + delta`) + 4 invariants. |
| `diagnostic_audit.py` | Read-only name/temporal/dedup audits; writes `V<version>_diagnostic_audit_report.md`. |
| `build_explorer.py` | `--version`-aware explorer builder from `explorer_template.html` + canonical + labels. |
| `networkx_diagnostic.py` | Read-only structural analysis (betweenness, trunk-roots + geodesics, floater recount); writes `networkx_diagnostic_v<version>.md` + `.json`. Lineage subgraph = person↔person. Self-tests need a baseline refresh (§5). |

**Merge invocation (no new scripts, no baseline edits):**
`phase_i_merge.py --expansion <batch>.json --manifest-a <A|empty>.json --manifest-b <B|empty>.json --version v<N> --config pipeline_config.json` → `phase_g_labels.py --config …` → `phase_h_apply.py --version v<N> --run-record merge_run_v<N>.json --config …` → `diagnostic_audit.py --version v<N> --config …` → `build_explorer.py --version v<N>`.

**Analysis invocation (read-only):** `networkx_diagnostic.py --version v<N> --config pipeline_config.json [--threshold 5 --top-n 25]`.

Archived (`archive/`, flat): spent per-version pipeline scripts and batch inputs (incl. V13/V14/V15 expansions + no-op manifests). `backups/` holds per-merge rollback snapshots.
