# Surgical Lineage Atlas — Unified Plan
## v11

**Author:** Ankit Sarin, MD
**Date:** 2026-05-30
**Status:** Graph at 509 edges / 394 nodes / 1 component after the V11 Pittsburgh/Starzl transplant expansion plus the founding-year and directionality cleanup. Explorer rebuilt and back in sync (durable template + builder + current output, verified live in-browser). Single-component invariant held.

---

## 1. What This Is

A citation-backed directed knowledge graph mapping the training lineages, institutional founding chains, and professional society networks of American surgery from 1777 through the present. The project sits at the intersection of digital humanities, surgical history, and network science, with goals spanning academic publication, open dataset contribution, and surgical education. Operates under the Digital Surgeon research initiative brand.

## 2. Architecture

**Graph schema (v3):** JSON edge arrays conforming to `00_schema.json` (JSON Schema draft-07). **Eight edge types:** `direct_training`, `observational_study`, `institutional_founder`, `institutional_succession`, `society_founder`, `governance_leadership`, `programmatic_accreditation`, and `institutional_parent` (added in Task 2B). Three node types: `person`, `institution`, `society`. Four evidence types: `PMID`, `DOI`, `institutional_archive`, and `society_verified` (pending schema addition for society-provided training records).

**Storage:** 15 module files — 14 thematic modules (`01_halsted_core.json` through `14_global_military.json`) plus `15_institutional_hierarchy.json` (the dedicated architectural module for `institutional_parent` edges). Supporting files: canonical flat file (`surgical_lineage_graph_canonical.json`, regenerated from the 15 modules), auxiliary node metadata file (`node_labels_adjudicated.json` — carries `label_short` display names for the D3 explorer; not part of the edge module system and not included in canonical regeneration).

**Visualization (rebuilt V11):** Single-file D3.js interactive explorer, now back in sync and split into a durable template + data builder. `explorer_v11_template.html` is the design-of-record — data left as a `PLACEHOLDER`, with all conventions baked in (Digital Surgeon palette/typography, node coloring/shape by type, degree-scaled radius, logarithmic two-tier zoom-dependent labels, force params, evidence toggle, arrowhead trimming) plus first-class `institutional_parent` rendering: recessed structural styling, a "Hierarchy" toolbar toggle (default on), and parent-chain highlighting up to root on institution select. `build_explorer.py` regenerates `surgical_lineage_atlas_v11.html` from current canonical + node labels, computing live header stats. Future graph versions are a builder re-run against the same template — no UI rework.

**Analysis pipeline (planned):** NetworkX for betweenness centrality, shortest-path analysis between independent trunk roots, and connected component enumeration.

**Division of labor:** This chat (Claude) handles architecture, planning, research, JSON drafting, and prompt authoring. Claude Code on MacBook handles file operations, module edits, canonical regeneration, verification pipelines, and explorer rebuild.

**Key methodological decisions:**
- Training edges restricted to documented PD and APD roles only — informal mentors without structural titles are excluded
- `observational_study` edges restricted to pre-1950 era (when no fellowship alternative existed), with the Mouret→Dubois→Reddick chain grandfathered as a verified exception
- `direct_training` is the correct edge type for pre-FC MIS fellowships (structured training under named mentor, regardless of FC accreditation status)
- Evidence tier hierarchy: PMID > DOI > society_verified > institutional_archive
- Citation verification: all PMIDs require content-match validation, not just existence checks. Final bibliographic verification runs through citation-mcp (`bulkVerifyCitations` against Crossref/PubMed/OpenAlex/Semantic Scholar) before any citation enters a module; web search alone is not sufficient for final lock
- **`governance_leadership` directionality (codified V10, anomalies resolved V11):** person → (institution | society) — the chair/leader/president is the source, the organization the target. The V11 audit confirmed 122 of 126 edges conform; the four nonconformers were resolved — the two person→person edges deleted, the single institution→person outlier (Mayo Clinic Department of Surgery→Wilson) reversed, and the lone society→institution edge (ACS→Surgical Care Improvement Project) retained as legitimate (a society governing a program, not an anomaly)
- PMCID storage convention: `evidence_type: "PMID"`, `evidence_citation: "PMCID: PMCxxxxxxx"`
- For large module files exceeding Claude Code's read limit (~10K tokens), use `jq` for duplicate checks and edge insertion rather than reading the full file into context
- **Canonical naming rule (codified Task 2B):** One root node per real-world institution. Sub-unit format: `<Root Name> <Sub-unit Descriptor>`. Root name must exactly prefix every child ID within the cluster. Short labels live in `node_labels_adjudicated.json`, preserving zoom-dependent rendering
- **End-year convention for structural-hierarchy edges:** `end_year: 2026` paired with `temporal_range: "<start>-ongoing"` for currently-active `institutional_parent` relationships. 2026 figure refreshed on demand. No `9999` sentinel
- **institutional_parent start_year convention (revised V10, fully applied V11):** `start_year` is the sub-unit's documented founding/establishment year — the structural-temporal fact — and is independent of which sources happen to be PMID-indexed. Evidence type and temporal anchor are decoupled: `institutional_archive` is the appropriate and accepted evidence for organizational founding events, with PMID/DOI used only where a source genuinely documents the founding itself. A later chair's tenure start is never used as a proxy for the sub-unit's founding year
- **Architectural metadata separation:** `institutional_parent` edges route to `15_institutional_hierarchy.json`, not thematic modules. Training, founding, governance, succession, and accreditation edges continue to route thematically

## 3. Current State

| Metric | Value |
|--------|-------|
| Total edges | 509 |
| Total nodes | 394 (persons 206, institutions 133, societies 55) |
| Modules | 15 (14 thematic + 1 architectural) |
| Schema version | v3 (8 edge types) |
| Connected components | 1 |
| Build phases completed | Original through V6, citation verification Phases 1–2.5, V7–V9 merges, Task 2B (schema v3 + hierarchy retrofit), V10 departmental expansion, V11 Pittsburgh/Starzl expansion + founding-year/directionality cleanup, explorer rebuild |
| Explorer version | V11 (rebuilt, in sync; template + builder + verified output) |

**Edge type distribution (post-V11):**

| Edge Type | Count |
|-----------|------:|
| direct_training | 133 |
| governance_leadership | 132 |
| institutional_founder | 93 |
| society_founder | 61 |
| institutional_parent | 37 |
| programmatic_accreditation | 24 |
| institutional_succession | 18 |
| observational_study | 11 |

**Collaborator group:**

| Person | Institution | Role | Active Task |
|--------|------------|------|-------------|
| Ankit Sarin | UC Davis | PI, graph architect | NetworkX analysis pipeline, continued expansion, manuscript |
| Adnan Alseidi | UCSF | ACS board liaison, HPB connections | ACS dissemination positioning |
| Talar Tatarian | Jefferson | FC data lead | FC data request letter |
| Nova Szoka | WVU | MIS/fellowship hypothesis | MIS lineage conceptual framework |

## 4. What Changed This Session (V10 → V11)

V11 Pittsburgh/Starzl transplant expansion merged 2026-05-30. Graph grew 491/378/1 → 509/394/1: +21 batch edges − 3 semantic deletes = +18 edges; +16 nodes (7 persons, 9 institutions). Single-component invariant held; acceptance gate clean (0 duplicate triples, 0 node-type conflicts, 1 component).

- **Starzl transplant lineage deepened.** Seven `direct_training` edges (Shaw, Klintmalm, Todo, Abu-Elmagd, Scantlebury, Reyes, Shapiro), three `institutional_founder` (UNMC Transplant Program, Baylor University Medical Center Transplant Program, Pitt Intestinal Transplant Program), seven `governance_leadership` (including Klintmalm→ASTS), and four `institutional_parent` edges. Tzakis and Fung were found already deepened in the baseline — no action. New bridges into existing clusters: Reyes→UW Department of Surgery, Abu-Elmagd→Cleveland Clinic, Klintmalm→ASTS.
- **Citations.** One citation-mcp-verified PMID (Scantlebury, PMID 29461461, *Transplantation* 2018); the remaining 20 edges use `institutional_archive` (the Starzl archive at starzl.pitt.edu and official university/program histories — legitimate per the founding/biographical allowance, not citation-mcp-verifiable). PMID-upgrade candidates flagged: Abu-Elmagd intestinal series, Todo FK-506 papers.
- **Founding-year corrections (Manifest A).** Five `institutional_parent` start_years corrected from chair/citation proxies to documented founding years, all → `institutional_archive`: UMN 1930→1906, Illinois 1936→1937, UC Davis 1978→1966, Baylor (Houston) 1948→1943, Pittsburgh 1964→1886 (new finding — General Surgery was an original 1886 department).
- **Semantic/directionality cleanup (Manifest B).** Deleted Wangensteen→Najarian (factual error — Najarian was the recruited successor), Kirk→Bunnell (redundant), and Bahnson→Starzl (person→person violation); reversed Mayo Clinic Department of Surgery→Wilson to Wilson→Mayo Clinic; reclassified Bahnson→Pitt Department of Surgery from `institutional_founder` to `governance_leadership` (1963–1987, the second full-time chair).
- **Merge mechanics.** Built `v11_phase_i_merge.py` (adds thematic-module routing with relaxed per-route edge-type contract; adds `edge_modify_fields` and `edge_semantic_ops` manifest handlers with `expected_existing` guards). Ran `v10_phase_g_labels.py` (16 new stubs), `v10_phase_h_apply.py` (canonical regen + NetworkX gate), and `v10_diagnostic_audit.py` re-baselined to 509/394. Audit flagged 3 multi-type source→target pairs (Hart/Duke, Mathews/Proctologic, Matas/ACS) — confirmed legitimate founder+leader pattern, all pre-existing.
- **Explorer rebuilt.** Produced the reusable `explorer_v11_template.html` (five V11 deltas baked in), the `build_explorer.py` builder, and `surgical_lineage_atlas_v11.html` (509/394, verified live in-browser: recessed parent edges, working Hierarchy toggle, parent-chain highlight, live stats).
- **Repo hygiene.** Git milestone commit (author corrected to Ankit Sarin / dr.ankitsarin@gmail.com); the four spent v10 phase scripts moved to `archive/`; diagnostic report renamed V10→V11 with `REPORT_PATH`/title repointed; `.claude/launch.json` to be gitignored.

## 5. Open Issues & Blockers

1. **`society_verified` evidence type not yet in schema** — needs addition to `00_schema.json` before any society data ingestion (Fellowship Council partnership).
2. **FC data request letter not yet drafted** — Talar owns this.
3. **Label regeneration pending** — ~67 stubs in `node_labels_adjudicated.json` (51 prior + 16 from V11), all `reviewed: false`. Deferred to a dedicated label task with programmatic short-label derivation.
4. **V11 approximate-year confirmations (moderate confidence):** Klintmalm→ASTS (~2005 — Ankit to verify exact presidency term), Abu-Elmagd→Cleveland Clinic (~2015), Scantlebury→University of South Alabama (~2002). Plus optional PMID upgrades for the Abu-Elmagd intestinal series and Todo FK-506 papers. Bundle into a small correction manifest.
5. **Canonical descriptor cleanup (low priority):** existing items (`Baylor College of Medicine Cardiovascular Surgery` → `...Division of...`; `Peter Bent Brigham Peripheral Vascular Clinic` prefix break) plus the V11 leaf nodes (Hokkaido University, University of South Alabama, Mount Sinai Recanati/Miller Transplantation Institute) which may want root-plus-sub-unit tidying.
6. **Deferred edge re-attempts / data nits pending better sourcing:** Moore→Blaisdell (only if Lim *Arch Surg* 2000 full text documents the Brigham year); Graham→Cole (only with a content-matched training source); minor accuracy review of Tzakis→University of Miami Transplant Program (founder 1994 vs the program's ~1970 origin) and Fung→University of Chicago (governance vs founding-director framing).

## 6. Next Steps

1. **NetworkX analysis pipeline** — betweenness centrality, shortest-path analysis between independent trunk roots, floating-person recount against the current 394-node graph. Now the primary manuscript-blocking item (explorer is done).
2. **Continue institutional expansion** — Cornell/New York Hospital, Washington University, Northwestern, WVU, ordered by floating-person anchoring value; deepen thin degree-1 departments (UAB, Cincinnati, Stanford). MIS training lineages as an independent thread (Nova's conceptual framework).
3. **`society_verified` schema addition + FC data request letter** (Talar) — unblocks the Fellowship Council proof-of-concept partnership.
4. **V11 cleanup manifest** — confirm the three approximate years and apply the optional PMID upgrades (Open Issue 4).
5. **Label regeneration pass** (~67 stubs).
6. **Manuscript drafting** — begin once the NetworkX outputs land (the analytical core of the paper).

## 7. Publishing & Dissemination Path

**Manuscript:** Knowledge graph structural analysis (not a history paper). Core contributions: betweenness centrality identifying non-obvious bridge figures, shortest-path analysis between independent trunk roots, and the complete census of American surgical subspecialty society-to-board spawning events. The institutional hierarchy layer enables multi-tier traversal analyses (how training relationships cross organizational levels) that were not previously queryable.

**Target journals (ranked):**
1. *Journal of Surgical Education* (Elsevier, Q1) — primary target; covered under UC open access agreement
2. *Surgery* (Elsevier) — higher impact backup; also UC OA covered
3. *Medical Teacher* (Taylor & Francis) — cost-advantaged if needed; UC OA covered

**Dissemination:**
- ACS Clinical Congress presentation (Adnan to surface when timing is right)
- SAGES presentation (natural fit given MIS expansion)
- Interactive explorer as supplementary material or standalone web resource

## 8. Workflow Convention

**Planning environment:** Claude chat (this project). Architecture, research, email drafting, expansion specifications, manuscript strategy.

**Execution environment:** Claude Code on MacBook. File operations, module edits, canonical regeneration, verification pipelines, explorer rebuild.

**The core loop (claude.ai authors, Claude Code merges):** this chat does the thinking and produces the artifacts — research and PubMed/web discovery, contrarian scope review, schema decisions, and the authored JSON: a route-tagged expansion file (`route:` annotation in each edge's notes pointing to its destination module) plus separate match/replace manifests for any modifications to existing edges. Every bibliographic citation is verified through citation-mcp before it enters an artifact. The chat does **not** run file operations or merges. Claude Code on the MacBook takes those files (dropped into the `2026 Surgical lineage` folder), backs up the touched modules, and merges them using the tested phase scripts, then regenerates the canonical, runs the audit, and reports the result back here for the next step.

**Iterative process:** Outline → Web search (offer proactively) → Confirm → Expand → Refine. One batch at a time, explicit approval before proceeding.

**Citation discipline:** discovery via web/PubMed search (citation-mcp cannot find unknown sources); final verification via citation-mcp (`bulkVerifyCitations` over the pooled set) before any citation enters a module. Content-match against full text where the supporting claim is specific (governance spans, training relationships) and the abstract is absent. `institutional_archive` is the accepted evidence type for founding events and biographical facts not present in indexed databases.

**Expansion file convention:** consolidated expansion file(s) plus separate match/replace manifests for edge modifications, with a `route:` annotation in each edge's notes field. For `institutional_parent` edges, target module is `15_institutional_hierarchy.json`. Manifest operation vocabulary now includes `modify_fields` (guarded field updates), `delete`, `reverse_retarget`, and `reclassify`, each with `expected_existing` guards.

**Batch workflow:** accumulate expansion/manifest files in claude.ai chat, download to the MacBook `2026 Surgical lineage` folder, single Claude Code merge pass that **reuses the tested phase scripts** (insertion, label stubs, regeneration, audit) rather than hand-rolling logic. Back up touched files first. Avoid repeated canonical regeneration. Low-blast-radius file/Python tasks run with `--dangerously-skip-permissions`; never git/systemd/system-level config.

**Explorer pattern (durable):** `explorer_v11_template.html` is the design-of-record (data as `PLACEHOLDER`, all conventions + `institutional_parent` rendering baked in); `build_explorer.py` regenerates `surgical_lineage_atlas_v<graphver>.html` from current canonical + node labels. Future graph versions = re-run the builder; no UI rework. The v5 template and v8 instance are retained as references.

## 9. Execution Scripts (retained on MacBook)

| Script | Purpose |
|--------|---------|
| `v11_phase_i_merge.py` | V11 batch merge — thematic-module routing with relaxed per-route edge-type contract, pre-insert duplicate-triple check, and `edge_modify_fields` / `edge_semantic_ops` manifest handlers with `expected_existing` guards |
| `v10_phase_g_labels.py` | Label file stub generation for new and missing nodes (reused in V11) |
| `v10_phase_h_apply.py` | Canonical regeneration and NetworkX invariant validation (reused, re-baselined to 509/394) |
| `v10_diagnostic_audit.py` | Read-only audit (canonical names, temporal, dedup, connected components); re-baselined to 509/394; writes `V11_diagnostic_audit_report.md` |
| `build_explorer.py` | Repeatable explorer builder — canonical + node labels → injected into `explorer_v11_template.html` → `surgical_lineage_atlas_v11.html` |

Archived (`archive/`): the four spent one-time v10 migrations — `v10_phase_b_retrofit.py`, `v10_phase_e_rename.py`, `v10_phase_f_hierarchy.py`, and the superseded `v10_phase_i_merge.py`. All retained scripts are re-runnable. Latest backup at `backups/v11_merge_20260530_175155/`.
