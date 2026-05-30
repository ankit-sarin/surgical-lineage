# Task 2B Retrofit Report
Generated: 2026-04-19T10:33:46Z

## Schema
v3 live (`institutional_parent` in enum) — applied in prior Task 2 Phase A.

## Renames (Phase E)
- `Johns Hopkins Department of Neurosurgery` → `Johns Hopkins Hospital Department of Neurosurgery` (id-field edge substitutions: 2)
- `Johns Hopkins Neurosurgery Residency Program` → `Johns Hopkins Hospital Neurosurgery Residency Program` (id-field edge substitutions: 2)
- Total id-field substitutions across modules: 4
- Additional note-text substitutions (descriptive references inside `notes` fields): 1
- Label file entries updated: 1

## New bare root nodes (10)
- Cleveland Clinic
- Johns Hopkins Hospital
- Massachusetts General Hospital
- Mayo Clinic
- Peter Bent Brigham Hospital
- University of Miami
- University of Minnesota
- University of Pennsylvania
- University of Pittsburgh
- Washington University

Memorial Sloan Kettering Cancer Center was already present; not counted as new.

## `institutional_parent` edges authored: 28
Routed to: `15_institutional_hierarchy.json` (new module).

## Label file
- Pre-task entries: 327
- Stub entries added: 44 (10 new bare roots + 34 pre-existing gaps)
- Post-task entries: 371 (matches canonical node count)
- All stubs have `label_short: ""`, `label_short_source: "stub_pending_adjudication"`, `reviewed: false`
- No pre-existing entry was modified (verified by SHA-256 hash of the first 327 entries)

## Graph state
- Edges: 452 → 480 (+28)
- Nodes: 361 → 371 (+10)
- Components: 1 (invariant held)

## Deferred (out of scope for this task)
- Programmatic short-label derivation (full label regeneration for the 44 stubs)
- `Peter Bent Brigham Peripheral Vascular Clinic` naming cleanup (inconsistent with other PBB Hospital children, which use "Hospital" in their ID)
- V10 department-level `institutional_parent` edges (e.g., Minnesota Dept of Surgery → University of Minnesota) — authored during V10 departmental work
- Mediterranean Theater Surgical Service still has no parent; theater-level meta-node class modeling deferred

## Module inventory
- `01_halsted_core.json`: 15 edges
- `02_general_surgery_spread.json`: 112 edges
- `03_neurosurgery.json`: 32 edges
- `04_cardiothoracic_vascular.json`: 33 edges
- `05_urology.json`: 12 edges
- `06_orthopedics.json`: 12 edges
- `07_oncology_trials.json`: 20 edges
- `08_subspecialties.json`: 74 edges
- `09_trauma_acute_infection.json`: 20 edges
- `10_quality_outcomes.json`: 23 edges
- `11_mis_robotic.json`: 13 edges
- `12_governance_societies.json`: 66 edges
- `13_pre_halsted.json`: 5 edges
- `14_global_military.json`: 15 edges
- `15_institutional_hierarchy.json`: 28 edges

## Edge-type distribution
- `direct_training`: 126
- `governance_leadership`: 121
- `institutional_founder`: 91
- `society_founder`: 61
- `institutional_parent`: 28
- `programmatic_accreditation`: 24
- `institutional_succession`: 18
- `observational_study`: 11
