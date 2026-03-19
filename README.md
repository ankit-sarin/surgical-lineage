# Surgical Lineage Atlas — Knowledge Graph Data

A knowledge graph tracing the lineage of American surgery from its pre-Halstedian roots through the modern era of subspecialization, clinical trials networks, and quality improvement science. The graph captures training relationships, institutional foundings, society governance, and programmatic accreditation across 318 nodes and 382 edges spanning 1777–2026.

## Schema

### Node Types
- **person** — Individual surgeons, physicians, and scientists
- **institution** — Departments of surgery, hospitals, research programs
- **society** — Professional societies, boards, and associations

### Edge Types
- **direct_training** — Formal residency or fellowship training relationship
- **observational_study** — Observership or visiting scholar relationship
- **institutional_founder** — Founded or established an institution
- **institutional_succession** — One institution evolved into or was replaced by another
- **society_founder** — Founded a professional society
- **governance_leadership** — Served in a leadership role (president, chair, etc.)
- **programmatic_accreditation** — One organization accredits or oversees another

### Evidence Types
- **PMID** — PubMed-indexed publication (204 edges)
- **DOI** — Digital Object Identifier (9 edges)
- **institutional_archive** — Institutional archive, registry, or official history (169 edges)

## Module Index

| File | Thematic Scope | Edges |
|------|---------------|-------|
| `01_halsted_core.json` | Halsted core — the root of the American surgical lineage tree | 15 |
| `02_general_surgery_spread.json` | General surgery spread — how Halstedian surgery spread to major institutions | 100 |
| `03_neurosurgery.json` | Neurosurgery — Cushing and downstream neurosurgical lineage | 15 |
| `04_cardiothoracic_vascular.json` | Cardiothoracic and vascular surgery | 28 |
| `05_urology.json` | Urology | 9 |
| `06_orthopedics.json` | Orthopedic surgery | 12 |
| `07_oncology_trials.json` | Oncology and clinical trials networks | 20 |
| `08_subspecialties.json` | Subspecialties — colorectal, pediatric, plastic, endocrine, HPB, bariatric | 58 |
| `09_trauma_acute_infection.json` | Trauma, acute care surgery, and surgical infection | 20 |
| `10_quality_outcomes.json` | Quality improvement and outcomes science | 22 |
| `11_mis_robotic.json` | Minimally invasive and robotic surgery | 9 |
| `12_governance_societies.json` | Governance and professional societies | 57 |
| `13_pre_halsted.json` | Pre-Halsted surgery — the predecessors | 5 |
| `14_global_military.json` | Global and military surgery | 12 |
| **Total** | | **382** |

### Supporting Files

| File | Description |
|------|-------------|
| `00_schema.json` | JSON Schema (draft-07) defining edge object structure |
| `99_pmid_upgrade_manifest.json` | Archive of PMID/DOI citation upgrades applied during build |
| `surgical_lineage_graph_canonical.json` | Flat file of all 382 edges sorted by start_year, with module field — consumed by D3 visualization |

## Provenance

Consolidated from 50 source files (01–54) created across two build phases. V3 expansion integrated 8 expansion files (27 new edges) and 6 citation upgrade manifests (16 upgrades). V4 expansion integrated 5 expansion files (17 new edges), 1 upgrade manifest (7 PMID upgrades), and 1 audit file (3 corrections including the Churchill training lineage correction). Phase 2.5 citation upgrade campaign (2026-03-18) upgraded 34 edges from institutional_archive to PMID, reverted 1 edge (Blakemore) back to institutional_archive, resolved 9 verification flags, and corrected 1 structural error (Ponsky→SAGES reclassified from society_founder to governance_leadership; Gerald Marks identified as true SAGES founder).

## Data Quality

- Zero duplicate edges
- Zero node-type inconsistencies
- All evidence types normalized to schema enum (PMID, DOI, institutional_archive)
- 204 of 382 edges backed by PubMed-indexed citations (53.4%)
- 9 of 382 edges backed by DOI citations
- 169 of 382 edges backed by institutional_archive (44.2%)
- Wikipedia citations: 0 (last one eliminated in V3)

## Citation Verification Status

**Phase 1 completed:** 2026-03-17

| Metric | Count |
|--------|-------|
| Unique PMIDs checked | 137 |
| PMID edges verified | 201 |
| Unique DOIs checked | 8 |
| DOI edges verified | 9 |
| Verification failures (edges) | 3 |
| Failure breakdown | 2 PMID (15354259, 19763730) + 1 DOI (10.1007/s00268-022-06710-1) |
| Archive edges (pending Phase 2) | 172 |

Failures flagged with `[VERIFY_FAILED]` stamps in edge notes and downgraded to `confidence: low` for manual review.

**Phase 1.5 completed:** 2026-03-17

| Metric | Count |
|--------|-------|
| Content matches | 97 |
| Weak matches (flagged) | 51 |
| Mismatches (flagged) | 60 |

Mismatches downgraded to `confidence: low` and stamped with `MISMATCH` in edge notes. Weak matches stamped with `weak_match` and matched/missed tokens for manual review. Full details in `verification_report_phase1_5.json`.

**Phase 1.75 completed:** 2026-03-17 — PubMed/CrossRef search for replacement candidates for all 111 flagged edges. Results in `CITATION_REPAIR_CANDIDATES.md` and `citation_repair_candidates.json`. Manually adjudicated via `citation_adjudicator.html`.

**Phase 2 completed:** 2026-03-17 — applied adjudicated repairs

| Metric | Count |
|--------|-------|
| Citations replaced (ACCEPT) | 52 |
| Downgraded to archive (ARCHIVE) | 32 |
| Edges deleted (DELETE) | 4 |
| Citations retained (KEEP) | 23 |
| Total edges post-Phase 2 | 381 |
| Re-verification passes | 52 |
| Re-verification failures | 0 |

All 52 newly inserted PMIDs/DOIs passed both existence and content-match re-verification. Full details in `verification_report_phase2.json`.

**Phase 2.5 completed:** 2026-03-18 — PubMed search campaign to upgrade institutional_archive edges to verified PMIDs

| Metric | Count |
|--------|-------|
| Upgrades attempted | 35 |
| Successfully applied | 34 |
| Reverted to institutional_archive | 1 (Blakemore — training dates post-Halsted death) |
| Verification flags resolved | 9 (8 cleared, 1 reverted) |
| Structural corrections | 1 (Ponsky→SAGES reclassified; Marks→SAGES created) |
| New edges added | 1 (Gerald Marks→SAGES society_founder) |
| Edges backed by PMID post-Phase 2.5 | 204 (53.4%) |
| Edges backed by institutional_archive post-Phase 2.5 | 169 (44.2%) |

The campaign processed 7 changeset files (batch1–batch7) covering 12 module files. Nine edges initially flagged verification_required were resolved through secondary-source verification: 8 confirmed (notes appended), 1 reverted (Hopkins→Blakemore, whose 1922–1926 training dates begin the year Halsted died). The Ponsky→SAGES society_founder edge was reclassified to governance_leadership (SAGES president 1990–91) per PMID 29362909, which identifies Gerald Marks as the true SAGES founder (1981).

## Changelog

- **2026-03-18** — Phase 2.5 citation upgrade campaign: upgraded 34 edges from institutional_archive to verified PMIDs across 12 module files (7 changeset batches). Resolved 9 verification flags (8 confirmed via secondary sources, 1 reverted). Reverted Hopkins→Blakemore to institutional_archive (training dates 1922–1926 post-Halsted death; Carter 1952 cannot confirm). Structural correction: Ponsky→SAGES reclassified from society_founder to governance_leadership (SAGES president 1990–91) per PMID 29362909; new Gerald Marks→SAGES society_founder edge created (SAGES founded 1981). Graph: 382 edges, 318 nodes. PMID-backed edges: 204 (53.4%, up from 44.1%). New node: Gerald Marks.
- **2026-03-17** — V5 expansion: merged 25 expansion files (two planning sessions) adding 65 new edges and 1 citation upgrade (Holman→Stanford PMID upgrade), bringing the graph to 385 edges and 319 nodes across 14 modules (1 pre-existing cross-module duplicate removed: Cushing→Elkin in 03_neurosurgery superseded by richer version in 02_general_surgery_spread). New structural features: Sabiston training tree (8 trainees including Wolfe, Bollinger, Cox, Spray, Chitwood, Anderson, Jones), Blalock training tree (Haller, Hanlon, Jude, Muller, Ravitch, Scott, Longmire), DeBakey training tree (Crawford, Noon, Mattox, Morris, Garrett, Creech), Wangensteen training tree (Lillehei, Lewis, Merendino, Najarian, Varco, Buchwald, Shumway, Mason), plastic surgery bridge (Blair→Brown→Barrett→ABPS), Hunter/Physick pre-Halsted bridge, Kocher Nobel lineage, Rhoads/Penn lineage, Zollinger/Ohio State lineage, Reemtsma/Columbia lineage, Folkman angiogenesis, Brennan/MSK, Silen/Beth Israel, UCSF chain, Stanford chain, Vanderbilt depth, Emory depth, Michigan succession, Hopkins modern succession, Mattox/Ben Taub trauma, Nyhus hernia, Organ/URM, Hendren/MGH, 5 component bridges (small islands batch). Connected components reduced from 6 to 3. PMID verification: 18/23 passed, 3 soft passes (subjects in article body), 2 PMIDs corrected: 18294269 (wrong article; Folkman obituary has no PMID, upgraded to DOI 10.1016/j.jpedsurg.2008.01.016), 33421312 (wrong article; St. Mark's training program article has no PMID, upgraded to DOI 10.1007/bf02586849). PMID 37601473 confirmed correct (Ann Surg Open, not Plast Reconstr Surg). DOI 10.1007/s10029-009-0522-1 verified (no associated PMID). Validated: zero duplicates, full schema compliance.
- **2026-03-16** — V4 expansion: integrated 17 new edges (5 expansion files), 7 PMID citation upgrades (1 manifest), and 3 corrections (1 audit file). Churchill training lineage corrected (Richardson replaces Cushing). New structural features: complete colorectal surgery lineage (Turnbull/Fazio/Cleveland Clinic/ABCRS), 4 component bridges reducing components from 14 to 10 (Phemister→ASA, Hopkins→Flint, Blumgart→MSK, Brigham Dept→Transplant), Freischlag as first woman Hopkins surgeon-in-chief and ACS president, Pellegrini at UW, Fonkalsrud extending Blalock→Longmire chain, FES→ABS credentialing chain. Graph: 321 edges, 282 nodes. Validated: zero duplicates, full schema compliance.
- **2026-03-16** — V3 expansion: integrated 27 new edges (8 expansion files) and 16 citation upgrades (6 manifests) from gap analysis session. New structural features: kidney transplant origin (Murray/Brigham), first training edges for women (Cole→Jonasson, Morrow→Braunwald), three-generation URM lineage (Whipple→Drew→Leffall), acute care surgery fellowship formalization (AAST→ACS Fellowship), West Coast depth (Debas/UCSF, Shumway/Stanford), MIS module governance bridge (Ponsky→ABS). Wikipedia citation eliminated (Ravdin→Fisher). Graph: 304 edges, 273 nodes. Validated: zero duplicates, full schema compliance.
- **2026-03-15** — Consolidated 50 source files into 14 thematic modules. Applied graph_update_draft (removed 2 edges, added 2 edges). Normalized 2 non-standard evidence_type values. Applied outstanding PMID upgrades from manifest. Validated: 249 edges, 228 nodes, zero duplicates, full schema compliance.
