# Surgical Lineage Atlas — Unified Plan
## v10

**Author:** Ankit Sarin, MD
**Date:** 2026-05-30
**Status:** Graph at 491 edges / 378 nodes / 1 component after the V10 departmental expansion batch (Minnesota, Baylor, UC Davis, Illinois). All new edges PMID/DOI-grounded and bulk-verified via citation-mcp. Single-component invariant held.

---

## 1. What This Is

A citation-backed directed knowledge graph mapping the training lineages, institutional founding chains, and professional society networks of American surgery from 1777 through the present. The project sits at the intersection of digital humanities, surgical history, and network science, with goals spanning academic publication, open dataset contribution, and surgical education. Operates under the Digital Surgeon research initiative brand.

## 2. Architecture

**Graph schema (v3):** JSON edge arrays conforming to `00_schema.json` (JSON Schema draft-07). **Eight edge types:** `direct_training`, `observational_study`, `institutional_founder`, `institutional_succession`, `society_founder`, `governance_leadership`, `programmatic_accreditation`, and `institutional_parent` (added in Task 2B). Three node types: `person`, `institution`, `society`. Four evidence types: `PMID`, `DOI`, `institutional_archive`, and `society_verified` (pending schema addition for society-provided training records).

**Storage:** 15 module files — 14 thematic modules (`01_halsted_core.json` through `14_global_military.json`) plus `15_institutional_hierarchy.json` (the dedicated architectural module for `institutional_parent` edges). Supporting files: canonical flat file (`surgical_lineage_graph_canonical.json`, regenerated from the 15 modules), auxiliary node metadata file (`node_labels_adjudicated.json` — carries `label_short` display names for the D3 explorer; not part of the edge module system and not included in canonical regeneration).

**Visualization:** Single-file D3.js interactive explorer. Current deployed version is V5 (out of sync). V8 rebuild spec defined but not yet executed — requires stripping the V5 embedded JSON payload to create a rendering template, then Claude Code rebuilds against current canonical. Explorer visual spec: edge styling by type (including the institutional_parent edge type), two-tier zoom-dependent labels (`label_short` at low zoom, full canonical ID at high zoom), evidence toggle with colored badges (green=PMID, blue=DOI, gray=archive), tooltips as positioned divs, node sizing by degree, node coloring by type using Digital Surgeon palette.

**Analysis pipeline (planned):** NetworkX for betweenness centrality, shortest-path analysis between independent trunk roots, and connected component enumeration.

**Division of labor:** This chat (Claude) handles architecture, planning, research, JSON drafting, and prompt authoring. Claude Code on MacBook handles file operations, module edits, canonical regeneration, verification pipelines, and explorer rebuild.

**Key methodological decisions:**
- Training edges restricted to documented PD and APD roles only — informal mentors without structural titles are excluded
- `observational_study` edges restricted to pre-1950 era (when no fellowship alternative existed), with the Mouret→Dubois→Reddick chain grandfathered as a verified exception
- `direct_training` is the correct edge type for pre-FC MIS fellowships (structured training under named mentor, regardless of FC accreditation status)
- Evidence tier hierarchy: PMID > DOI > society_verified > institutional_archive
- Citation verification: all PMIDs require content-match validation, not just existence checks. Final bibliographic verification runs through citation-mcp (`bulkVerifyCitations` against Crossref/PubMed/OpenAlex/Semantic Scholar) before any citation enters a module; web search alone is not sufficient for final lock
- **`governance_leadership` directionality (codified V10):** person → institution (the chair/leader is the source, the institution the target). Dominant in 72 of 76 edges and in all 33 chair-to-department edges. The two reversed outliers (institution → person) and the two person → person edges are flagged anomalies, not the convention
- PMCID storage convention: `evidence_type: "PMID"`, `evidence_citation: "PMCID: PMCxxxxxxx"`
- For large module files exceeding Claude Code's read limit (~10K tokens), use `jq` for duplicate checks and edge insertion rather than reading the full file into context
- **Canonical naming rule (codified Task 2B):** One root node per real-world institution. Sub-unit format: `<Root Name> <Sub-unit Descriptor>`. Root name must exactly prefix every child ID within the cluster. Short labels live in `node_labels_adjudicated.json`, preserving zoom-dependent rendering
- **End-year convention for structural-hierarchy edges:** `end_year: 2026` paired with `temporal_range: "<start>-ongoing"` for currently-active `institutional_parent` relationships. 2026 figure refreshed on demand. No `9999` sentinel
- **institutional_parent start_year convention (revised V10):** `start_year` is the sub-unit's documented founding/establishment year — the structural-temporal fact — and is independent of which sources happen to be PMID-indexed. Evidence type and temporal anchor are decoupled: `institutional_archive` is the appropriate and accepted evidence for organizational founding events (per the schema's pre-MEDLINE/founding-event allowance), with PMID/DOI used only where a source genuinely documents the founding itself. A later chair's tenure start is never used as a proxy for the sub-unit's founding year. Rationale: published literature in surgical history is sparse and uneven; anchoring temporal facts to citation availability would distort the betweenness and era-slicing analyses the project exists to produce
- **Architectural metadata separation:** `institutional_parent` edges route to `15_institutional_hierarchy.json`, not thematic modules. Training, founding, governance, succession, and accreditation edges continue to route thematically

## 3. Current State

| Metric | Value |
|--------|-------|
| Total edges | 491 |
| Total nodes | 378 (persons ~199, institutions ~124, societies ~55) |
| Modules | 15 (14 thematic + 1 architectural) |
| Schema version | v3 (8 edge types) |
| Connected components | 1 |
| Build phases completed | Original through V6, citation verification Phases 1–2.5, V7–V9 merges, Task 2B (schema v3 + hierarchy retrofit), V10 departmental expansion batch |
| Explorer version | V5 (out of sync — rebuild spec ready, not yet executed) |

**Edge type distribution (post-V10):**

| Edge Type | Count |
|-----------|------:|
| direct_training | 127 |
| governance_leadership | 126 |
| institutional_founder | 91 |
| society_founder | 61 |
| institutional_parent | 33 |
| programmatic_accreditation | 24 |
| institutional_succession | 18 |
| observational_study | 11 |

**Collaborator group:**

| Person | Institution | Role | Active Task |
|--------|------------|------|-------------|
| Ankit Sarin | UC Davis | PI, graph architect | V11 Pittsburgh, semantic cleanup pass, manuscript |
| Adnan Alseidi | UCSF | ACS board liaison, HPB connections | ACS dissemination positioning |
| Talar Tatarian | Jefferson | FC data lead | FC data request letter |
| Nova Szoka | WVU | MIS/fellowship hypothesis | MIS lineage conceptual framework |

## 4. What Changed This Session (V9 → V10)

V10 departmental expansion batch merged 2026-05-30. Graph grew 480/371/1 → 491/378/1, adding 11 edges and 7 nodes across four institutional clusters, with two re-parent modifications. Research pass applied contrarian scope discipline at each cluster:

- **Minnesota.** Discovered the cluster was already rich — Wangensteen, Najarian, Lillehei, Barnard and most of their lineage edges were already present. The real gap was the absence of a Department of Surgery node. Added it with Wangensteen (chair 1930–1967, PMID 17972214) and Najarian (chair 1967–1993, DOI 10.1111/ctr.14877) governance edges plus the parent edge, and re-parented the existing Open Heart and Transplant programs under the Department (3-tier hierarchy). **Dropped** a proposed Lillehei CV-division node: the CT fellowship was ACGME-accredited only from 1988 (two decades after Lillehei left in 1967), and his only division-chief framing is a present-day endowed title — anachronistic. Barnard moved to the deferred audit (already anchored via the existing Lillehei→Barnard edge).
- **Baylor.** DeBakey was a degree-11 hub with no institutional home — the same anomaly Wangensteen had. Added Baylor College of Medicine (root) + Department of Surgery node + DeBakey chair governance (1948–1993, PMID 28285665), and anchored the previously-floating Baylor CV sub-unit under the Department.
- **UC Davis.** Entered *anchored* (not as an isolated home-institution appendage) via F. William Blaisdell (new node, chair 1978–1995, PMID 32649610), bridged into the main component by a DeBakey→Blaisdell cardiovascular-fellowship `direct_training` edge. A Moore→Blaisdell (Peter Bent Brigham) edge asserted by web obituaries was **dropped** after the peer-reviewed J Trauma tribute (full text, PMID 32649610) failed to corroborate it — a content-match catch that overrode an initial instruction to include both training edges.
- **Illinois.** Fixed the one truly bare Department node via Warren Cole chair governance (1936–1966, PMID 11685200) + root + parent, raising the existing Cole node from degree 1 to 2. A Graham→Cole training edge was **deferred** — sources document cholecystography collaboration, not a content-matched training relationship.

All five citations bulk-verified high-confidence via citation-mcp. Two canonical corrections recorded: the Najarian Festschrift resolves to PMID 36528870, canonical year 2022 (not 2023); the Cole tribute resolves to PMID 11685200 / DOI 10.1067/msy.2001.114146 (Cance WG, Surgery 2001). `governance_leadership` directionality was confirmed and codified. Merge executed via a new `v10_phase_i_merge.py`; `v10_diagnostic_audit.py` was adapted to baseline 491/378, include module 15, and report connected components. Six files backed up; SHA-256 confirmed the prior 371 label entries were untouched.

**Post-merge architectural correction.** The institutional_parent start_year convention was revised (start_year = documented founding year, not earliest citable PMID — see Section 2). As a consequence, four of the five V10 parent-edge start_years are flagged for correction to true founding years: UMN Dept (1930→1906, known), Baylor Dept (1948→needs verification), UC Davis Dept (1978→needs verification), Illinois Dept (1936→needs verification). Baylor CV→Baylor Dept (1948) is correct and unchanged. Correction is the first cleanup task next session (see Open Issues / Next Steps).

## 5. Open Issues & Blockers

1. **Explorer out of sync (V5 vs current 491/378 data)** — rebuild spec ready, not yet executed. `explorer_v5_template.html` exists in the working folder. Manuscript-blocking.
2. **`society_verified` evidence type not yet in schema** — needs addition to `00_schema.json` before any society data ingestion (Fellowship Council partnership).
3. **FC data request letter not yet drafted** — Talar owns this.
4. **Label regeneration pending** — 51 stubs in `node_labels_adjudicated.json` (44 from Task 2B + 7 from V10), all `reviewed: false`. Deferred to a dedicated label task with programmatic short-label derivation.
5. **Semantic / directionality cleanup (consolidated):** (a) Wangensteen→Najarian `direct_training` is a confirmed factual error — Najarian was the recruited successor, not a trainee; delete it. (b) Bahnson→Starzl 1981 is a person→person `governance_leadership` violation. (c) Two reversed `governance_leadership` outliers (Mayo Clinic Dept→Wilson + one other). A single read-only audit + fix pass should address all three classes before V11.
6. **Canonical descriptor renames (low priority):** `Baylor College of Medicine Cardiovascular Surgery` → `...Division of Cardiovascular Surgery`; `Peter Bent Brigham Peripheral Vascular Clinic` breaks the cluster's "Hospital" prefix pattern.
7. **Deferred edge re-attempts pending better sourcing:** Moore→Blaisdell (only if Lim *Arch Surg* 2000 full text documents the Brigham training year); Graham→Cole (only with a content-matched training source).
8. **V10 parent-edge start_year correction (near-term):** four institutional_parent start_years were merged with citation-anchored years instead of true founding years (see Section 4). UMN Dept → 1906 is known; Baylor Dept, UC Davis Dept, and Illinois Dept founding years need a brief verification pass, then a correction manifest. `institutional_archive` is the appropriate evidence type for these founding dates.

## 6. Next Steps

1. **V11 Pittsburgh expansion** — Starzl transplant lineage depth, paired with the Bahnson→Starzl semantic fix (item 5b).
2. **Parent-edge start_year correction + semantic/directionality cleanup pass** (Open Issues 5, 8) — Claude Code task, ideally bundled with or just before V11: verify true founding years for the Baylor, UC Davis, and Illinois departments (UMN = 1906 known) and correct the four parent-edge start_years to founding years with `institutional_archive` evidence; delete Wangensteen→Najarian; fix Bahnson→Starzl; correct the two reversed governance outliers.
3. **NetworkX analysis pipeline** — betweenness centrality, shortest-path analysis between independent trunk roots, floating-person recount against the current 378-node graph. Manuscript-blocking alongside the explorer.
4. **Explorer rebuild** against current canonical, extended to render the `institutional_parent` edge type.
5. **Continue institutional expansion** — Cornell/New York Hospital, Washington University, Northwestern, WVU, ordered by floating-person anchoring value; deepen thin degree-1 departments (UAB, Cincinnati, Stanford).
6. **Label regeneration pass** (51 stubs).
7. **`society_verified` schema addition + FC data request letter** (Talar) — unblocks the Fellowship Council proof-of-concept partnership.

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

**Iterative process:** Outline → Web search (offer proactively) → Confirm → Expand → Refine. One batch at a time, explicit approval before proceeding.

**Citation discipline:** discovery via web/PubMed search (citation-mcp cannot find unknown sources); final verification via citation-mcp (`bulkVerifyCitations` over the pooled set) before any citation enters a module. Content-match against full text where the supporting claim is specific (governance spans, training relationships) and the abstract is absent.

**Expansion file convention:** consolidated expansion file(s) plus a separate match/replace manifest for edge modifications, with a `route:` annotation in each edge's notes field. For `institutional_parent` edges, target module is `15_institutional_hierarchy.json`.

**Batch workflow:** accumulate expansion/manifest files in claude.ai chat, download to the MacBook `2026 Surgical lineage` folder, single Claude Code merge pass that **reuses the tested phase scripts** (insertion, label stubs, regeneration, audit) rather than hand-rolling logic. Back up touched files first. Avoid repeated canonical regeneration.

**Explorer rebuild workflow:** (1) `explorer_v5_template.html` already created (V5 with JSON payload stripped). (2) Claude Code reads template as reference for D3 rendering logic. (3) Claude Code injects current canonical + node labels, outputs updated HTML. Needs one-time extension to render the `institutional_parent` edge type.

## 9. Execution Scripts (retained on MacBook)

| Script | Purpose |
|--------|---------|
| `v10_diagnostic_audit.py` | Read-only audit (canonical names, temporal, dedup, connected components). Adapted in V10 to baseline 491/378 and include module 15 |
| `v10_phase_e_rename.py` | Node rename across modules and label file |
| `v10_phase_f_hierarchy.py` | `institutional_parent` edge authorship and evidence inheritance |
| `v10_phase_g_labels.py` | Label file stub generation for new and missing nodes |
| `v10_phase_h_apply.py` | Canonical regeneration and NetworkX invariant validation |
| `v10_phase_i_merge.py` | V10 batch merge — `route:`-tagged insertion with pre-insert duplicate check + reparent-manifest application |

All scripts are re-runnable. Latest backup at `backups/v10_merge_20260530_134305/`.
