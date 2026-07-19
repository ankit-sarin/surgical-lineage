# NetworkX Structural Diagnostic — v13 (interim)

Read-only analysis. Canonical sha256 `b4e141be1ef52bffd3f6990614f701e5c4a3c9398aa5827125daf57e94a795ba` (unchanged after run: YES).
Graph: 415 nodes / 552 raw edges / 549 simple directed edges (3 parallel collapsed) / 1 component(s).
Parameters: threshold=5, top-n=25.

> Interim diagnostic on a still-growing graph — provisional numbers, not a manuscript lock.

## 1 — Betweenness centrality (normalized)

Full-graph tables annotate `node_type`: institution/society dominance is *why* manuscript lineage claims anchor on the training projection, not the full graph. `G_train` is the corrected **person↔person** lineage projection (both endpoints person); non-person training edges are excluded — see the REVIEW section.

### G_full (directed, all types) — top 25

| Node | Type | Betweenness | In | Out |
|---|---|---|---|---|
| American College of Surgeons | society | 0.0414 | 26 | 10 |
| ACS National Surgical Quality Improvement Program | institution | 0.0392 | 4 | 2 |
| Johns Hopkins Hospital Department of Surgery | institution | 0.0351 | 5 | 10 |
| Alfred Blalock | person | 0.0122 | 2 | 10 |
| Thomas Starzl | person | 0.0113 | 1 | 13 |
| Mayo Clinic Department of Surgery | institution | 0.0100 | 3 | 3 |
| LaSalle D. Leffall Jr. | person | 0.0098 | 3 | 2 |
| Owen Wangensteen | person | 0.0091 | 1 | 9 |
| Memorial Sloan Kettering Cancer Center | institution | 0.0053 | 4 | 1 |
| American Society for Metabolic and Bariatric Surgery | society | 0.0046 | 2 | 1 |
| John L. Cameron | person | 0.0040 | 1 | 4 |
| David Sabiston | person | 0.0038 | 1 | 8 |
| Edward Mason | person | 0.0036 | 1 | 2 |
| American Society for Bariatric Surgery | society | 0.0035 | 1 | 1 |
| William Longmire | person | 0.0030 | 1 | 3 |
| Kathryn D. Anderson | person | 0.0026 | 1 | 3 |
| Keith D. Lillemoe | person | 0.0023 | 1 | 2 |
| Robert E. Gross | person | 0.0023 | 2 | 5 |
| Joseph E. Murray | person | 0.0022 | 1 | 2 |
| Massachusetts General Hospital Department of Surgery | institution | 0.0021 | 4 | 2 |
| William Stewart Halsted | person | 0.0020 | 1 | 11 |
| UCLA Department of Surgery | institution | 0.0020 | 1 | 1 |
| W. Hardy Hendren III | person | 0.0019 | 1 | 2 |
| Murray F. Brennan | person | 0.0016 | 1 | 3 |
| Patrick Walsh | person | 0.0016 | 1 | 3 |

### G_full_u (undirected, all types) — top 25

| Node | Type | Betweenness | In | Out |
|---|---|---|---|---|
| American College of Surgeons | society | 0.4464 | 36 | 36 |
| Johns Hopkins Hospital Department of Surgery | institution | 0.2705 | 14 | 14 |
| American Surgical Association | society | 0.1904 | 19 | 19 |
| William Stewart Halsted | person | 0.1509 | 12 | 12 |
| American Board of Surgery | society | 0.1390 | 12 | 12 |
| Thomas Starzl | person | 0.1300 | 14 | 14 |
| American Board of Medical Specialties | society | 0.1269 | 9 | 9 |
| ACS National Surgical Quality Improvement Program | institution | 0.1121 | 6 | 6 |
| Harvey Cushing | person | 0.1065 | 12 | 12 |
| Michael DeBakey | person | 0.1026 | 14 | 14 |
| Owen Wangensteen | person | 0.0812 | 10 | 10 |
| Mayo Clinic Department of Surgery | institution | 0.0768 | 6 | 6 |
| David Sabiston | person | 0.0761 | 9 | 9 |
| John L. Cameron | person | 0.0725 | 4 | 4 |
| Society of American Gastrointestinal and Endoscopic Surgeons | society | 0.0699 | 10 | 10 |
| Alfred Blalock | person | 0.0610 | 12 | 12 |
| American Association for Thoracic Surgery | society | 0.0583 | 9 | 9 |
| American Society of Colon and Rectal Surgeons | society | 0.0525 | 5 | 5 |
| Evarts A. Graham | person | 0.0432 | 6 | 6 |
| American Board of Orthopaedic Surgery | society | 0.0404 | 2 | 2 |
| American Orthopaedic Association | society | 0.0400 | 4 | 4 |
| Society of Neurological Surgeons | society | 0.0377 | 4 | 4 |
| Julie Ann Freischlag | person | 0.0371 | 3 | 3 |
| Bernard Fisher | person | 0.0359 | 3 | 3 |
| LaSalle D. Leffall Jr. | person | 0.0331 | 4 | 4 |

### G_train (directed person↔person lineage projection) — top 25

| Node | Type | Betweenness | In | Out |
|---|---|---|---|---|
| William Stewart Halsted | person | 0.0025 | 1 | 10 |
| Harvey Cushing | person | 0.0024 | 2 | 7 |
| Robert E. Gross | person | 0.0019 | 2 | 4 |
| John Homans | person | 0.0013 | 1 | 1 |
| Theodor Billroth | person | 0.0010 | 1 | 1 |
| Alfred Blalock | person | 0.0009 | 1 | 10 |
| Theodor Kocher | person | 0.0007 | 1 | 1 |
| John Kirklin | person | 0.0006 | 1 | 2 |
| Michael DeBakey | person | 0.0006 | 1 | 9 |
| Elliott Cutler | person | 0.0005 | 1 | 2 |
| Walter Dandy | person | 0.0005 | 1 | 1 |
| David Sabiston | person | 0.0004 | 1 | 4 |
| A. Earl Walker | person | 0.0003 | 1 | 1 |
| W. Hardy Hendren III | person | 0.0003 | 1 | 1 |
| Wilder Penfield | person | 0.0003 | 1 | 1 |
| E. Stanley Crawford | person | 0.0002 | 1 | 2 |
| Mont Reid | person | 0.0002 | 1 | 1 |
| Denton Cooley | person | 0.0001 | 2 | 1 |
| Edward Churchill | person | 0.0001 | 1 | 1 |
| Francis D. Moore | person | 0.0001 | 1 | 1 |
| Harold Gillies | person | 0.0001 | 1 | 2 |
| William Longmire | person | 0.0001 | 1 | 1 |
| C. Walton Lillehei | person | 0.0001 | 1 | 1 |
| Charles R. Drew | person | 0.0001 | 1 | 1 |
| Francois Dubois | person | 0.0001 | 1 | 1 |

### G_train_u (undirected person↔person lineage projection) — top 25

| Node | Type | Betweenness | In | Out |
|---|---|---|---|---|
| William Stewart Halsted | person | 0.0438 | 11 | 11 |
| Harvey Cushing | person | 0.0345 | 9 | 9 |
| Alfred Blalock | person | 0.0310 | 11 | 11 |
| Robert E. Gross | person | 0.0248 | 6 | 6 |
| John Homans | person | 0.0242 | 2 | 2 |
| Michael DeBakey | person | 0.0238 | 10 | 10 |
| Denton Cooley | person | 0.0206 | 3 | 3 |
| David Sabiston | person | 0.0109 | 5 | 5 |
| Elliott Cutler | person | 0.0070 | 3 | 3 |
| John Kirklin | person | 0.0070 | 3 | 3 |
| Walter Dandy | person | 0.0069 | 2 | 2 |
| E. Stanley Crawford | person | 0.0057 | 3 | 3 |
| Thomas Starzl | person | 0.0039 | 9 | 9 |
| A. Earl Walker | person | 0.0035 | 2 | 2 |
| Mont Reid | person | 0.0035 | 2 | 2 |
| Owen Wangensteen | person | 0.0035 | 7 | 7 |
| W. Hardy Hendren III | person | 0.0035 | 2 | 2 |
| Wilder Penfield | person | 0.0035 | 2 | 2 |
| William Longmire | person | 0.0029 | 2 | 2 |
| Theodor Billroth | person | 0.0021 | 2 | 2 |
| Theodor Kocher | person | 0.0013 | 2 | 2 |
| C. Walton Lillehei | person | 0.0009 | 2 | 2 |
| Norman Shumway | person | 0.0009 | 2 | 2 |
| Harold Gillies | person | 0.0005 | 3 | 3 |
| John Najarian | person | 0.0003 | 3 | 3 |

## 2 — Trunk roots (person↔person lineage projection)

`G_train` = training edges (`direct_training`, `observational_study`) with **both endpoints person**: 138 nodes / 119 edges.
Weakly-connected components: 24 total; 5 major (size ≥ 5, 5 components); 7 major trunk root(s) — all persons.

> **Definitional fix (V13-DIAG-FIX).** The prior run filtered on edge_type alone, pulling 27 non-person training edges into the projection (chiefly institution→person `direct_training`) and seating institutions (Mayo/JHH/Howard/MSK departments) as trunk roots. Restricting to person↔person yields the correct **138 nodes / 24 weak components / 5 components ≥ 5**, with all trunk roots persons. Excluded edges enumerated in the REVIEW section.

### Major trunk roots (components size ≥ threshold)

| Comp # | Size | Edges | Root(s) |
|---|---|---|---|
| 0 | 35 | 37 | Bernhard von Langenbeck, William E. Ladd |
| 1 | 29 | 29 | Alton Ochsner, Helen Taussig |
| 2 | 10 | 10 | Owen Wangensteen |
| 3 | 10 | 9 | Thomas Starzl |
| 4 | 5 | 4 | Vilray Blair |

### Full census (all components)

| Comp # | Size | Edges | Major | Root(s) |
|---|---|---|---|---|
| 0 | 35 | 37 | Y | Bernhard von Langenbeck, William E. Ladd |
| 1 | 29 | 29 | Y | Alton Ochsner, Helen Taussig |
| 2 | 10 | 10 | Y | Owen Wangensteen |
| 3 | 10 | 9 | Y | Thomas Starzl |
| 4 | 5 | 4 | Y | Vilray Blair |
| 5 | 4 | 3 |  | Edward P. Richardson |
| 6 | 4 | 3 |  | I.S. Ravdin |
| 7 | 4 | 3 |  | John Najarian |
| 8 | 3 | 2 |  | Allen O. Whipple |
| 9 | 3 | 2 |  | Charles Frazier |
| 10 | 3 | 2 |  | John Hunter |
| 11 | 3 | 2 |  | Philippe Mouret |
| 12 | 3 | 2 |  | Rupert B. Turnbull |
| 13 | 2 | 1 |  | Andrew Morrow |
| 14 | 2 | 1 |  | Arthur Blakemore |
| 15 | 2 | 1 |  | Charles Elsberg |
| 16 | 2 | 1 |  | Ernest Sachs |
| 17 | 2 | 1 |  | Evarts A. Graham |
| 18 | 2 | 1 |  | Henry Harkins |
| 19 | 2 | 1 |  | John Charnley |
| 20 | 2 | 1 |  | John L. Cameron |
| 21 | 2 | 1 |  | Patrick Walsh |
| 22 | 2 | 1 |  | Warren Cole |
| 23 | 2 | 1 |  | William J. Mayo |

## 3 — Root-to-root geodesics (undirected, full graph)

19 cross-trunk major-root pair(s). Unreachable: 0 (expected 0 given single component).

### Distance matrix

| | Bernhard… | William… | Alton Ochsner | Helen Taussig | Owen… | Thomas Starzl | Vilray Blair |
|---|---|---|---|---|---|---|---|
| Bernhard… | · | — | 5 | 5 | 6 | 4 | 7 |
| William… | — | · | 5 | 6 | 4 | 5 | 8 |
| Alton Ochsner | 5 | 5 | · | — | 4 | 4 | 5 |
| Helen Taussig | 5 | 6 | — | · | 4 | 3 | 7 |
| Owen… | 6 | 4 | 4 | 4 | · | 4 | 5 |
| Thomas Starzl | 4 | 5 | 4 | 3 | 4 | · | 7 |
| Vilray Blair | 7 | 8 | 5 | 7 | 5 | 7 | · |

### Per-pair geodesics

| A | B | Dist | Single-bridge | Path |
|---|---|---|---|---|
| Helen Taussig | Thomas Starzl | 3 |  | Helen Taussig → Alfred Blalock → Johns Hopkins Hospital Department of Surgery → Thomas Starzl |
| Alton Ochsner | Owen Wangensteen | 4 |  | Alton Ochsner → American College of Surgeons → ACS National Surgical Quality Improvement Program → Mayo Clinic Department of Surgery → Owen Wangensteen |
| Alton Ochsner | Thomas Starzl | 4 |  | Alton Ochsner → American College of Surgeons → John L. Cameron → Johns Hopkins Hospital Department of Surgery → Thomas Starzl |
| Bernhard von Langenbeck | Thomas Starzl | 4 |  | Bernhard von Langenbeck → Theodor Billroth → William Stewart Halsted → Johns Hopkins Hospital Department of Surgery → Thomas Starzl |
| Helen Taussig | Owen Wangensteen | 4 |  | Helen Taussig → Alfred Blalock → Henry Bahnson → American Surgical Association → Owen Wangensteen |
| Owen Wangensteen | Thomas Starzl | 4 |  | Owen Wangensteen → American Surgical Association → John L. Cameron → Johns Hopkins Hospital Department of Surgery → Thomas Starzl |
| William E. Ladd | Owen Wangensteen | 4 |  | William E. Ladd → Robert E. Gross → John Kirklin → Mayo Clinic Department of Surgery → Owen Wangensteen |
| Alton Ochsner | Vilray Blair | 5 |  | Alton Ochsner → American College of Surgeons → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| Bernhard von Langenbeck | Alton Ochsner | 5 |  | Bernhard von Langenbeck → Theodor Billroth → William Stewart Halsted → Emile Holman → Society for Vascular Surgery → Alton Ochsner |
| Bernhard von Langenbeck | Helen Taussig | 5 |  | Bernhard von Langenbeck → Theodor Billroth → William Stewart Halsted → Johns Hopkins Hospital Department of Surgery → Alfred Blalock → Helen Taussig |
| Owen Wangensteen | Vilray Blair | 5 |  | Owen Wangensteen → American Surgical Association → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| William E. Ladd | Alton Ochsner | 5 |  | William E. Ladd → Boston Children's Hospital Department of Surgery → W. Hardy Hendren III → Kathryn D. Anderson → American College of Surgeons → Alton Ochsner |
| William E. Ladd | Thomas Starzl | 5 |  | William E. Ladd → Robert E. Gross → John Homans → William Stewart Halsted → Johns Hopkins Hospital Department of Surgery → Thomas Starzl |
| Bernhard von Langenbeck | Owen Wangensteen | 6 |  | Bernhard von Langenbeck → Theodor Billroth → William Stewart Halsted → Johns Hopkins Hospital Department of Surgery → John L. Cameron → American Surgical Association → Owen Wangensteen |
| William E. Ladd | Helen Taussig | 6 |  | William E. Ladd → Robert E. Gross → John Homans → William Stewart Halsted → Johns Hopkins Hospital Department of Surgery → Alfred Blalock → Helen Taussig |
| Bernhard von Langenbeck | Vilray Blair | 7 |  | Bernhard von Langenbeck → Theodor Billroth → William Stewart Halsted → Howard Naffziger → American Board of Neurological Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| Helen Taussig | Vilray Blair | 7 |  | Helen Taussig → Alfred Blalock → Denton Cooley → American College of Surgeons → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| Thomas Starzl | Vilray Blair | 7 |  | Thomas Starzl → Andreas Tzakis → University of Miami Transplant Program → University of Miami → University of Miami Division of Plastic Surgery → D. Ralph Millard → Harold Gillies → Vilray Blair |
| William E. Ladd | Vilray Blair | 8 |  | William E. Ladd → Robert E. Gross → John Kirklin → American Association for Thoracic Surgery → Evarts A. Graham → Washington University Department of Surgery → Washington University → Washington University Division of Plastic Surgery → Vilray Blair |

### Top bridge intermediaries (geodesic interior-node frequency)

| Node | Times on a geodesic |
|---|---|
| Johns Hopkins Hospital Department of Surgery | 8 |
| William Stewart Halsted | 7 |
| Theodor Billroth | 5 |
| Alfred Blalock | 5 |
| American College of Surgeons | 5 |
| American Surgical Association | 4 |
| American Board of Medical Specialties | 4 |
| American Board of Plastic Surgery | 4 |
| Robert E. Gross | 4 |
| John L. Cameron | 3 |
| American Board of Surgery | 3 |
| John Homans | 2 |
| John Kirklin | 2 |
| Mayo Clinic Department of Surgery | 2 |
| Emile Holman | 1 |

## 4 — Floating-person recount (persons only)

Total persons: 212.

| Cut | Definition | Count |
|---|---|---|
| (a) full_degree1 | degree==1 in G_full_u | 53 (prior V11/V12 ~53) |
| (b) training_leaves | (in+out)≤1 in G_train | 170 |
|     ↳ training-isolated (deg 0) | no training edge at all | 74 |
|     ↳ training leaf (deg 1) | single training edge | 96 |
| (c) lineage_absent | 0 training edges, ≥1 non-training edge in G_full | 74 |

### Overlaps

- `full_degree1_AND_training_leaves`: 53
- `full_degree1_AND_lineage_absent`: 24
- `training_leaves_AND_lineage_absent`: 74

### Cut (c) lineage_absent — examples (in the atlas, in no lineage)

- Allan Kirk
- Barbara Lee Bass
- C. William Schwab
- Carlos A. Pellegrini
- Charles Scudder
- Chevalier Jackson
- Claude H. Organ Jr.
- Clifford Ko
- Curtice Rosser
- Dallas Phemister
- David Flum
- Diana Farmer
- Edward Delafield
- Eileen Bulger
- Ernest Codman
- Frank Lahey
- Franklin H. Martin
- Frederick Coller
- Frederick Salmon
- George Berci
- … (+54 more)

## Excluded non-person training edges (REVIEW)

27 training-type edge(s) (`direct_training` / `observational_study`) have a non-person endpoint and are therefore **excluded from the person↔person lineage projection**. `direct_training` is expected to run person↔person; institution-as-trainer is a data-model question flagged for adjudication — **not** edited or deleted here (out of scope).

Non-person sources appearing (institution/society as trainer): Johns Hopkins Hospital Department of Surgery (9), Jefferson Medical College Department of Surgery (2), Mayo Clinic Department of Surgery (2), St. Mark's Hospital for Fistula and Other Diseases of the Rectum (2), Columbia University Department of Surgery (1), Duke University Department of Surgery (1), Howard University Department of Surgery (1), Lahey Clinic (1), Massachusetts General Hospital Department of Surgery (1), Memorial Sloan Kettering Cancer Center (1), Peter Bent Brigham Hospital Department of Surgery (1), UCLA Department of Surgery (1), UCSF Department of Surgery (1), University of Michigan Department of Surgery (1), Mobile Army Surgical Hospital (MASH) System (1).

| Source | Src type | Target | Tgt type | Edge type | Module |
|---|---|---|---|---|---|
| Columbia University Department of Surgery | institution | Keith Reemtsma | person | direct_training | 02_general_surgery_spread.json |
| Duke University Department of Surgery | institution | Allan Kirk | person | direct_training | 02_general_surgery_spread.json |
| Howard University Department of Surgery | institution | LaSalle D. Leffall Jr. | person | direct_training | 02_general_surgery_spread.json |
| Jefferson Medical College Department of Surgery | institution | Chevalier Jackson | person | direct_training | 08_subspecialties.json |
| Jefferson Medical College Department of Surgery | institution | Samuel D. Gross | person | direct_training | 13_pre_halsted.json |
| Johns Hopkins Hospital Department of Surgery | institution | Alfred Blalock | person | direct_training | 01_halsted_core.json |
| Johns Hopkins Hospital Department of Surgery | institution | Arthur Blakemore | person | direct_training | 01_halsted_core.json |
| Johns Hopkins Hospital Department of Surgery | institution | Henry Harkins | person | direct_training | 02_general_surgery_spread.json |
| Johns Hopkins Hospital Department of Surgery | institution | J. Deryl Hart | person | direct_training | 01_halsted_core.json |
| Johns Hopkins Hospital Department of Surgery | institution | John L. Cameron | person | direct_training | 02_general_surgery_spread.json |
| Johns Hopkins Hospital Department of Surgery | institution | Joseph Marshall Flint | person | direct_training | 02_general_surgery_spread.json |
| Johns Hopkins Hospital Department of Surgery | institution | Peter Safar | person | direct_training | 02_general_surgery_spread.json |
| Johns Hopkins Hospital Department of Surgery | institution | Thomas Starzl | person | direct_training | 02_general_surgery_spread.json |
| Johns Hopkins Hospital Department of Surgery | institution | Warfield Firor | person | direct_training | 01_halsted_core.json |
| Lahey Clinic | institution | Victor W. Fazio | person | direct_training | 08_subspecialties.json |
| Massachusetts General Hospital Department of Surgery | institution | Frederick Coller | person | direct_training | 02_general_surgery_spread.json |
| Mayo Clinic Department of Surgery | institution | Owen Wangensteen | person | direct_training | 02_general_surgery_spread.json |
| Mayo Clinic Department of Surgery | institution | R. Lee Clark | person | direct_training | 07_oncology_trials.json |
| Memorial Sloan Kettering Cancer Center | institution | LaSalle D. Leffall Jr. | person | direct_training | 02_general_surgery_spread.json |
| Peter Bent Brigham Hospital Department of Surgery | institution | Murray F. Brennan | person | direct_training | 02_general_surgery_spread.json |
| UCLA Department of Surgery | institution | Patrick Walsh | person | direct_training | 05_urology.json |
| UCSF Department of Surgery | institution | William Silen | person | direct_training | 02_general_surgery_spread.json |
| University of Michigan Department of Surgery | institution | Norman Thompson | person | direct_training | 08_subspecialties.json |
| David Flum | person | The Dartmouth Institute for Health Policy and Clinical Practice | institution | observational_study | 10_quality_outcomes.json |
| Mobile Army Surgical Hospital (MASH) System | institution | Norman Rich | person | observational_study | 14_global_military.json |
| St. Mark's Hospital for Fistula and Other Diseases of the Rectum | institution | American Society of Colon and Rectal Surgeons | society | observational_study | 08_subspecialties.json |
| St. Mark's Hospital for Fistula and Other Diseases of the Rectum | institution | Joseph M. Mathews | person | observational_study | 08_subspecialties.json |

## Tests

| # | Test | Result | Detail |
|---|---|---|---|
| 1.G_train_all_persons | | **PASS** | every G_train node is a person |
| 2.G_train_138n_24wcc_5big | | **PASS** | nodes=138 (exp 138); weak_components=24 (exp 24); comps>=5: 5 (exp 5) |
| 3.trunk_roots_persons_and_match_reference | | **PASS** | major roots (7): ['Alton Ochsner', 'Bernhard von Langenbeck', 'Helen Taussig', 'Owen Wangensteen', 'Thomas Starzl', 'Vilray Blair', 'William E. Ladd']; all persons=True; matches reference 7-root set=True |
| 4.JohnHunter_indeg0_Halsted_indeg_ge1 | | **PASS** | John Hunter training in-degree=0 (exp 0); Halsted in-degree=1 (exp ≥1) |
| 5.full_degree1_53_and_Gfull_top5_unchanged | | **PASS** | full_degree1=53 (exp 53); G_full top-5=['American College of Surgeons', 'ACS National Surgical Quality Improvement Program', 'Johns Hopkins Hospital Department of Surgery', 'Alfred Blalock', 'Thomas Starzl']; unchanged=True |
| 6.excluded_nonperson_training_eq_27 | | **PASS** | excluded non-person training edges=27 (exp 27) |
| 7.canonical_sha_unchanged | | **PASS** | before=b4e141be1ef5… after=b4e141be1ef5… |
| S1.canonical_node_count_415 | | **PASS** | nodes=415; raw_edges=552; simple_edges=549 (collapsed 3) |
| S2.G_full_u_single_component | | **PASS** | components=1 |
| S3.betweenness_finite_all_4_graphs | | **PASS** | all four graphs finite & full coverage |
| S4.major_root_pairs_finite_distance | | **PASS** | 19 cross-trunk pairs; unreachable=0 |

