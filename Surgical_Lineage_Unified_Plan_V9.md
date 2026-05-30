# Surgical Lineage Atlas — Unified Plan
## v9

**Author:** Ankit Sarin, MD
**Date:** 2026-04-19
**Status:** Graph at 480 edges / 371 nodes / 1 component after Task 2B (schema v3 + institutional hierarchy retrofit). Canonical naming rule codified. V10 Minnesota research ready to begin.

---

## 1. What This Is

A citation-backed directed knowledge graph mapping the training lineages, institutional founding chains, and professional society networks of American surgery from 1777 through the present. The project sits at the intersection of digital humanities, surgical history, and network science, with goals spanning academic publication, open dataset contribution, and surgical education. Operates under the Digital Surgeon research initiative brand.

## 2. Architecture

**Graph schema (v3):** JSON edge arrays conforming to `00_schema.json` (JSON Schema draft-07). **Eight edge types:** `direct_training`, `observational_study`, `institutional_founder`, `institutional_succession`, `society_founder`, `governance_leadership`, `programmatic_accreditation`, and `institutional_parent` (added in Task 2B, 2026-04-19). Three node types: `person`, `institution`, `society`. Four evidence types: `PMID`, `DOI`, `institutional_archive`, and `society_verified` (pending schema addition for society-provided training records).

**Storage:** 15 module files now — 14 thematic modules (`01_halsted_core.json` through `14_global_military.json`) plus `15_institutional_hierarchy.json` (the dedicated architectural module for `institutional_parent` edges). Supporting files: canonical flat file (`surgical_lineage_graph_canonical.json`, regenerated from the 15 modules), auxiliary node metadata file (`node_labels_adjudicated.json` — carries `label_short` display names for the D3 explorer; not part of the edge module system and not included in canonical regeneration).

**Visualization:** Single-file D3.js interactive explorer. Current deployed version is V5 (out of sync). V8 rebuild spec defined but not yet executed — requires stripping the V5 embedded JSON payload to create a rendering template, then Claude Code rebuilds against current canonical. Explorer visual spec: edge styling by type (including the new institutional_parent edge type), two-tier zoom-dependent labels (`label_short` at low zoom, full canonical ID at high zoom), evidence toggle with colored badges (green=PMID, blue=DOI, gray=archive), tooltips as positioned divs, node sizing by degree, node coloring by type using Digital Surgeon palette.

**Analysis pipeline (planned):** NetworkX for betweenness centrality, shortest-path analysis between independent trunk roots, and connected component enumeration.

**Division of labor:** This chat (Claude) handles architecture, planning, research, JSON drafting, and prompt authoring. Claude Code on MacBook handles file operations, module edits, canonical regeneration, verification pipelines, and explorer rebuild.

**Key methodological decisions:**
- Training edges restricted to documented PD and APD roles only — informal mentors without structural titles are excluded
- `observational_study` edges restricted to pre-1950 era (when no fellowship alternative existed), with the Mouret→Dubois→Reddick chain grandfathered as a verified exception
- `direct_training` is the correct edge type for pre-FC MIS fellowships (structured training under named mentor, regardless of FC accreditation status)
- Evidence tier hierarchy: PMID > DOI > society_verified > institutional_archive
- Citation verification: all PMIDs require content-match validation, not just existence checks (hallucinated PMIDs pointing to unrelated articles are a known risk)
- PMCID storage convention: `evidence_type: "PMID"`, `evidence_citation: "PMCID: PMCxxxxxxx"`
- For large module files exceeding Claude Code's read limit (~10K tokens), use `jq` for duplicate checks and edge insertion rather than reading the full file into context
- **Canonical naming rule (codified Task 2B):** One root node per real-world institution. Sub-unit format: `<Root Name> <Sub-unit Descriptor>`. Root name must exactly prefix every child ID within the cluster. Short labels live in `node_labels_adjudicated.json`, preserving zoom-dependent rendering.
- **End-year convention for structural-hierarchy edges:** `end_year: 2026` paired with `temporal_range: "<start>-ongoing"` for currently-active `institutional_parent` relationships. 2026 figure refreshed on demand. No `9999` sentinel.
- **Architectural metadata separation:** `institutional_parent` edges route to `15_institutional_hierarchy.json`, not thematic modules. Training, founding, governance, succession, and accreditation edges continue to route thematically.

## 3. Current State

| Metric | Value |
|--------|-------|
| Total edges | 480 |
| Total nodes | 371 (persons ~198, institutions ~118, societies ~55) |
| Modules | 15 (14 thematic + 1 architectural) |
| Schema version | v3 (8 edge types) |
| Connected components | 1 |
| Build phases completed | Original through V6, citation verification Phases 1–2.5, V7–V9 merges, Task 2B (schema v3 + hierarchy retrofit) |
| Explorer version | V5 (out of sync — rebuild spec ready, not yet executed) |

**Edge type distribution (post-Task 2B):**

| Edge Type | Count |
|-----------|------:|
| direct_training | 126 |
| governance_leadership | 121 |
| institutional_founder | 91 |
| society_founder | 61 |
| institutional_parent | 28 |
| programmatic_accreditation | 24 |
| institutional_succession | 18 |
| observational_study | 11 |

**Collaborator group:**

| Person | Institution | Role | Active Task |
|--------|------------|------|-------------|
| Ankit Sarin | UC Davis | PI, graph architect | V10 Minnesota research, manuscript, APDCRS outreach |
| Adnan Alseidi | UCSF | ACS board liaison, HPB connections | ACS dissemination positioning |
| Talar Tatarian | Jefferson | FC data lead | FC data request letter |
| Nova Szoka | WVU | MIS/fellowship hypothesis | MIS lineage conceptual framework |

## 4. What Changed This Session (V8 → V9)

- **Task 2B — Schema v3 + Institutional Hierarchy Retrofit (2026-04-19).** Graph grew from 452/361/1 to 480/371/1 through the following operations:
  - **Schema v3 applied.** `institutional_parent` added to edge_type enum (7→8 values). Title bumped from "V2 Governance Expansion" to "V3 Institutional Hierarchy". Backup at `00_schema.v2.bak.json`.
  - **Pre-retrofit diagnostic audit (Task 1).** Read-only pass across canonical naming, temporal anomalies, and dedup discipline. Zero literal duplicates, zero temporal sentinels, zero logical inversions. Only one canonical-name pair above 0.95 similarity threshold (ACS NSQIP vs VA NSQIP, retained as legitimately distinct).
  - **Canonical naming rule codified.** Root institution naming, sub-unit format `<Root Name> <Sub-unit Descriptor>`, prefix-consistency enforcement within clusters. Johns Hopkins root adjudicated to "Johns Hopkins Hospital" (two node renames applied).
  - **10 new bare root nodes authored** for clusters that previously had no canonical parent: Washington University, Mayo Clinic, Massachusetts General Hospital, Peter Bent Brigham Hospital, Johns Hopkins Hospital, Cleveland Clinic, University of Miami, University of Minnesota, University of Pennsylvania, University of Pittsburgh.
  - **28 `institutional_parent` edges authored** across 11 parents (10 new + MSK CC, already present). Routed to new module `15_institutional_hierarchy.json`. Evidence inherited from each child's founder edge.
  - **Label file stubs added.** `node_labels_adjudicated.json` grew 327 → 371 (+44 stubs). All stubs marked `reviewed: false` and `label_short_source: "stub_pending_adjudication"`. First 327 entries hash-verified unchanged.
  - **Single-component invariant held.** NetworkX validated post-merge.

- **V10 institutional expansion plan established (pre-Task 2B).** 10+ target departments identified, prioritized by floating-person anchoring value.

## 5. Open Issues & Blockers

1. **Explorer out of sync (V5 vs V9 data)** — rebuild spec ready, not yet executed. `explorer_v5_template.html` exists in working folder. Manuscript-blocking.
2. **~58 person nodes have no institutional anchor** — count is approximate and pre-Task-2B. Fresh NetworkX floating-person recount deferred to V10 merge time. V10 institutional expansion targets this directly.
3. **`society_verified` evidence type not yet in schema** — needs addition to `00_schema.json` before any society data ingestion (Fellowship Council partnership).
4. **FC data request letter not yet drafted** — Talar owns this.
5. **Full label regeneration with programmatic short-label derivation** — 44 stubs in `node_labels_adjudicated.json` pending adjudication. Deferred to a dedicated label task.
6. **Bahnson → Starzl 1981 edge is a semantic violation** — `governance_leadership` between two person nodes (schema allows enum, semantic model does not). Recommended fix: delete and replace with `Starzl → University of Pittsburgh Transplant Program` (institutional_founder, parent node already exists), with Bahnson's recruitment captured in notes on the existing Bahnson → Pittsburgh governance edge. Scoped for near-term Claude Code task before V11.
7. **Systematic audit for person-to-person governance_leadership edges** — Bahnson→Starzl is unlikely to be unique. Read-only filter pass before V11.
8. **Peter Bent Brigham Peripheral Vascular Clinic** — name breaks the "Hospital" prefix pattern of the rest of the PBB cluster. Low-priority naming cleanup.
9. **V10 departmental institutional_parent edges** — authored during V10 departmental work, routed to `15_institutional_hierarchy.json`.

## 6. Next Steps

### V10 Institutional Expansion — immediate priority

Starts with University of Minnesota Department of Surgery (schema-compliant approach per the canonical naming rule; division nodes considered under the 1-of-3 gating criterion: accredited fellowship program, named endowed chair, or named-division documentation in a PMID-indexed history).

| Priority | Department | Floating Persons Anchored | Est. Edges (incl. divisions) |
|----------|-----------|--------------------------|-----------|
| 1A | University of Minnesota Dept of Surgery | Lillehei, Lewis, Barnard | 6–9 |
| 1B | Cornell/New York Hospital (Weill Cornell) | Lillehei (also here) | 4–5 |
| 1C | Washington University Dept of Surgery | Moyer, Cox | 4–5 |
| 2A | UC Davis Department of Surgery | (PI's institution) | 2–3 |
| 2B | West Virginia University Dept of Surgery | (collaborator Nova Szoka) | 2–3 |
| 2C | Northwestern University Dept of Surgery | Soper anchor | 3–4 |
| 3A-E | Brigham & Women's, Mount Sinai, Case Western, UVA, UT Southwestern | various | 2–3 each |

Also: deepen 16 thin departments (degree-1 institutional nodes), starting with UAB (Kirklin→Pacifico), Cincinnati (add Heuer as chair), Stanford (Shumway).

### Other pending

- Explorer rebuild (Claude Code task, spec ready)
- Label regeneration pass (programmatic short-labels + adjudication for 44 stubs)
- Bahnson→Starzl edge cleanup + systematic person→person governance audit
- Remaining V9 priorities not yet addressed: vascular board certification, endocrine surgery/AAES, Thomas Fogarty, bariatric surgery modern era

## 7. Publishing & Dissemination Path

**Manuscript:** Knowledge graph structural analysis (not a history paper). Core contributions: betweenness centrality identifying non-obvious bridge figures, shortest-path analysis between independent trunk roots, and the complete census of American surgical subspecialty society-to-board spawning events. The institutional hierarchy layer added in Task 2B enables multi-tier traversal analyses (e.g., how training relationships cross organizational levels) that were not previously queryable.

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

**Iterative process:** Outline → Web search (offer proactively) → Confirm → Expand → Refine. One batch at a time, explicit approval before proceeding.

**Expansion file convention:** `expansion_V[version]_T[tier]-[number]_[short_descriptor].json` with `TARGET MODULE:` annotation in each edge's notes field. For `institutional_parent` edges, target module is `15_institutional_hierarchy.json`.

**Batch workflow:** Accumulate all expansion/upgrade files in claude.ai chat, download to MacBook folder, single Claude Code merge pass with spec document. Avoid repeated canonical regeneration.

**Explorer rebuild workflow:** (1) `explorer_v5_template.html` already created (V5 with JSON payload stripped). (2) Claude Code reads template as reference for D3 rendering logic. (3) Claude Code injects current canonical + node labels, outputs updated HTML. Needs one-time extension to render the new `institutional_parent` edge type.

## 9. Task 2B Execution Scripts (retained on MacBook)

| Script | Purpose |
|--------|---------|
| `v10_diagnostic_audit.py` | Task 1 pre-retrofit read-only audit (canonical names, temporal, dedup) |
| `v10_phase_e_rename.py` | Johns Hopkins node rename across modules and label file |
| `v10_phase_f_hierarchy.py` | `institutional_parent` edge authorship and evidence inheritance |
| `v10_phase_g_labels.py` | Label file stub generation for new and missing nodes |
| `v10_phase_h_apply.py` | Canonical regeneration and NetworkX invariant validation |

All scripts are re-runnable. Backups at `backups/task2b_20260419_160000/`.
