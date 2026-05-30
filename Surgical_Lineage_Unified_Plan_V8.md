# Surgical Lineage Atlas — Unified Plan
## v8

**Author:** Ankit Sarin, MD  
**Date:** 2026-04-05  
**Status:** Graph at 452 edges / 361 nodes / 1 component after V9 merge. V10 institutional expansion plan drafted. Explorer rebuild spec ready (not yet executed).

---

## 1. What This Is

A citation-backed directed knowledge graph mapping the training lineages, institutional founding chains, and professional society networks of American surgery from 1777 through the present. The project sits at the intersection of digital humanities, surgical history, and network science, with goals spanning academic publication, open dataset contribution, and surgical education. Operates under the Digital Surgeon research initiative brand.

## 2. Architecture

**Graph schema:** JSON edge arrays conforming to `00_schema.json` (JSON Schema draft-07). Seven edge types: `direct_training`, `observational_study`, `institutional_founder`, `institutional_succession`, `society_founder`, `governance_leadership`, `programmatic_accreditation`. Three node types: `person`, `institution`, `society`. Four evidence types: `PMID`, `DOI`, `institutional_archive`, and `society_verified` (pending schema addition for society-provided training records).

**Storage:** 14 thematic module files (`01_halsted_core.json` through `14_global_military.json`) plus a canonical flat file and an auxiliary node metadata file (`node_labels_adjudicated.json` — carries `label_short` display names for the D3 explorer; not part of the edge module system and not included in canonical regeneration).

**Visualization:** Single-file D3.js interactive explorer. Current deployed version is V5 (out of sync). V8 rebuild spec defined — requires stripping the V5 embedded JSON payload to create a rendering template, then Claude Code rebuilds against current canonical. Explorer visual spec: edge styling by type, two-tier zoom-dependent labels (label_short at low zoom, full name at high zoom), evidence toggle with colored badges (green=PMID, blue=DOI, gray=archive), tooltips as positioned divs, node sizing by degree, node coloring by type using Digital Surgeon palette.

**Analysis pipeline (planned):** NetworkX for betweenness centrality, shortest-path analysis between independent trunk roots, and connected component enumeration.

**Division of labor:** This chat (Claude) handles architecture, planning, research, JSON drafting, and prompt authoring. Claude Code on MacBook handles file operations, module edits, canonical regeneration, verification pipelines, and explorer rebuild.

**Key methodological decisions:**
- Training edges restricted to documented PD and APD roles only — informal mentors without structural titles are excluded
- `observational_study` edges restricted to pre-1950 era (when no fellowship alternative existed), with the Mouret→Dubois→Reddick chain grandfathered as a verified exception
- `direct_training` is the correct edge type for pre-FC MIS fellowships (structured training under named mentor, regardless of FC accreditation status)
- Evidence tier hierarchy: PMID > DOI > society_verified > institutional_archive
- Citation verification: all PMIDs require content-match validation, not just existence checks (hallucinated PMIDs pointing to unrelated articles are a known risk)
- PMCID storage convention: `evidence_type: "PMID"`, `evidence_citation: "PMCID: PMCxxxxxxx"`
- For large module files exceeding Claude Code's read limit (~10K tokens), use `jq` for duplicate checks and edge insertion rather than reading the full file into context.

## 3. Current State

| Metric | Value |
|--------|-------|
| Total edges | 452 |
| Total nodes | 361 (persons ~210, institutions ~100, societies ~51) |
| PMID-backed edges | 268 (59.3%) |
| DOI-backed edges | 12 (2.7%) |
| institutional_archive edges | 172 (38.1%) |
| Connected components | 1 |
| Build phases completed | Original through V6, citation verification Phases 1–2.5, V7 merge, V8 merge, V9 merge |
| Explorer version | V5 (out of sync — rebuild spec ready, not yet executed) |
| Modules | 14 thematic files |

**Collaborator group:**

| Person | Institution | Role | Active Task |
|--------|------------|------|-------------|
| Ankit Sarin | UC Davis | PI, graph architect | Institutional expansion, manuscript, APDCRS outreach |
| Adnan Alseidi | UCSF | ACS board liaison, HPB connections | ACS dissemination positioning |
| Talar Tatarian | Jefferson | FC data lead | FC data request letter |
| Nova Szoka | WVU | MIS/fellowship hypothesis | MIS lineage conceptual framework |

## 4. What Changed This Session

- **V9 expansion: 29 new edges + 2 evidence upgrades across 5 expansion files and 1 upgrade manifest.** Graph grew from 423/340 to 452/361.
- **Track A (Matas/Vascular):** 5 edges. Rudolph Matas added as three-society bridge node (ACS co-founder + president, ASA president, AATS co-founder). First Tulane/New Orleans institutional node created. All backed by PMID 35412399.
- **Track B (MIS lineages):** 4 edges + 2 upgrades. Swanstrom, Soper, Schauer added as SAGES/ASMBS governance leaders. Legacy MIS Fellowship added as first named fellowship node in module 11. Soper→SAGES and Swanstrom→SAGES upgraded from institutional_archive to DOI (Brunt 2015 SAGES presidential address).
- **APSA/Joint Commission:** 4 edges + 1 addendum. Gross as first APSA president, Leape as co-founder, Anderson→APSA creating three-society governance bridge, ACS→JCAH closing the quality-improvement lineage from Codman. Koop→APSA added via upgrade manifest.
- **Neurosurgery extended:** 10 edges (8 initial + 2 bridge fix). Three independent lineage roots added beyond Cushing: Charles Frazier (Penn, 41 chairs), Charles Elsberg (Columbia/Neurological Institute, 36 chairs), Ernest Sachs (Wash U, 29 chairs). All backed by PMID 30218804. Bridge fix added Elsberg→SNS and Sachs→SNS to restore single connectivity.
- **ASCRS founding chain:** 5 edges. Complete lineage from St. Mark's London → Joseph Mathews → American Proctologic Society → ASCRS. Curtice Rosser as first ABCRS president. Turnbull→ASCRS governance. All backed by PMID 23997672.
- **Perissat excluded** from expansion — French, no American society roles, Dubois→Perissat would violate post-1950 observational_study restriction.
- **5 reference PDFs verified:** Ziechmann (PMID 30218804), Leape (PMID 8632263), Brunt (DOI 10.1007/s00464-015-4524-z), Field (PMID 35412399), Litynski (PMID 10444020). All uploaded to project files.
- **V10 institutional expansion plan drafted:** 10+ target departments identified, prioritized by floating-person anchoring value.

## 5. Open Issues & Blockers

1. **Explorer out of sync (V5 vs V9 data)** — rebuild spec ready, not yet executed. `explorer_v5_template.html` exists in working folder.
2. **58 person nodes have no institutional anchor** — 31% of persons float with only society/training edges. V10 institutional expansion targets this directly.
3. **`society_verified` evidence type not yet in schema** — needs addition to `00_schema.json` before any society data ingestion.
4. **FC data request letter not yet drafted** — Talar owns this.
5. **`node_labels_adjudicated.json` needs update** — 21 new nodes from V9 need label_short entries added.

## 6. Next Steps

**V10 Institutional Expansion (next session):**

| Priority | Department | Floating Persons Anchored | Est. Edges |
|----------|-----------|--------------------------|-----------|
| 1A | University of Minnesota Dept of Surgery | Lillehei, Lewis, Barnard | 5-6 |
| 1B | Cornell/New York Hospital (Weill Cornell) | Lillehei (also here) | 4-5 |
| 1C | Washington University/Barnes-Jewish Dept of Surgery | Moyer, Cox | 4-5 |
| 2A | UC Davis Department of Surgery | (PI's institution) | 2-3 |
| 2B | West Virginia University Dept of Surgery | (collaborator Nova Szoka) | 2-3 |
| 2C | Northwestern University Dept of Surgery | Soper anchor | 3-4 |
| 3A-E | Brigham & Women's, Mount Sinai, Case Western, UVA, UT Southwestern | various | 2-3 each |

Also: deepen 16 thin departments (degree-1 institutional nodes), starting with UAB (Kirklin→Pacifico), Cincinnati (add Heuer as chair), Stanford (Shumway).

**Other pending:**
- Explorer rebuild (Claude Code task, spec ready)
- Remaining V9 priorities not yet addressed: vascular board certification, endocrine surgery/AAES, Thomas Fogarty, bariatric surgery modern era
- Node labels adjudication for 21 new V9 nodes

## 7. Publishing & Dissemination Path

**Manuscript:** Knowledge graph structural analysis (not a history paper). Core contributions: betweenness centrality identifying non-obvious bridge figures, shortest-path analysis between independent trunk roots, and the complete census of American surgical subspecialty society-to-board spawning events.

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

**Expansion file convention:** `expansion_V[version]_T[tier]-[number]_[short_descriptor].json` with `TARGET MODULE:` annotation in each edge's notes field.

**Batch workflow:** Accumulate all expansion/upgrade files in claude.ai chat, download to MacBook folder, single Claude Code merge pass with spec document. Avoid repeated canonical regeneration.

**Explorer rebuild workflow:** (1) `explorer_v5_template.html` already created (V5 with JSON payload stripped). (2) Claude Code reads template as reference for D3 rendering logic. (3) Claude Code injects current canonical + node labels, outputs `surgical_lineage_atlas_v9.html`. Detailed architectural prompt in earlier chat history — search for "V8 Explorer Rebuild."
