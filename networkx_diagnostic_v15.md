# NetworkX Structural Diagnostic — v15 (interim)

Read-only analysis. Canonical sha256 `d13d038d8c3d3541a67fcad5d2533e5e863a8ecec5d6c7eadaadf87a43825eae` (unchanged after run: YES).
Graph: 428 nodes / 561 raw edges / 558 simple directed edges (3 parallel collapsed) / 1 component(s).
Parameters: threshold=5, top-n=25.

> Interim diagnostic on a still-growing graph — provisional numbers, not a manuscript lock.

## 1 — Betweenness centrality (normalized)

Full-graph tables annotate `node_type`: institution/society dominance is *why* manuscript lineage claims anchor on the training projection, not the full graph. `G_train` is the corrected **person↔person** lineage projection (both endpoints person); non-person training edges are excluded — see the REVIEW section.

### G_full (directed, all types) — top 25

| Node | Type | Betweenness | In | Out |
|---|---|---|---|---|
| American College of Surgeons | society | 0.0095 | 26 | 10 |
| ACS National Surgical Quality Improvement Program | institution | 0.0053 | 4 | 2 |
| Johns Hopkins Hospital Department of Surgery | institution | 0.0045 | 5 | 6 |
| Alfred Blalock | person | 0.0024 | 2 | 12 |
| LaSalle D. Leffall Jr. | person | 0.0017 | 3 | 2 |
| William Stewart Halsted | person | 0.0016 | 1 | 11 |
| Barney Brooks | person | 0.0013 | 1 | 2 |
| Mayo Clinic Department of Surgery | institution | 0.0011 | 3 | 2 |
| Memorial Sloan Kettering Cancer Center | institution | 0.0010 | 4 | 1 |
| American Board of Surgery | society | 0.0009 | 11 | 1 |
| Thomas Starzl | person | 0.0009 | 1 | 13 |
| American Society for Metabolic and Bariatric Surgery | society | 0.0009 | 2 | 1 |
| Society of American Gastrointestinal and Endoscopic Surgeons | society | 0.0009 | 8 | 2 |
| Robert E. Gross | person | 0.0008 | 2 | 5 |
| Theodor Billroth | person | 0.0008 | 1 | 2 |
| Kathryn D. Anderson | person | 0.0007 | 1 | 3 |
| John L. Cameron | person | 0.0007 | 2 | 4 |
| Peter Safar | person | 0.0007 | 1 | 2 |
| Arthur Blakemore | person | 0.0007 | 1 | 2 |
| American Board of Medical Specialties | society | 0.0006 | 8 | 1 |
| W. Hardy Hendren III | person | 0.0006 | 1 | 2 |
| Harvey Cushing | person | 0.0006 | 2 | 10 |
| Joseph E. Murray | person | 0.0005 | 1 | 2 |
| American Society for Bariatric Surgery | society | 0.0005 | 1 | 1 |
| Francis D. Moore | person | 0.0005 | 1 | 3 |

### G_full_u (undirected, all types) — top 25

| Node | Type | Betweenness | In | Out |
|---|---|---|---|---|
| American College of Surgeons | society | 0.4531 | 36 | 36 |
| American Surgical Association | society | 0.2061 | 19 | 19 |
| William Stewart Halsted | person | 0.1656 | 12 | 12 |
| Alfred Blalock | person | 0.1576 | 14 | 14 |
| Johns Hopkins Hospital Department of Surgery | institution | 0.1440 | 11 | 11 |
| American Board of Surgery | society | 0.1420 | 12 | 12 |
| Thomas Starzl | person | 0.1338 | 14 | 14 |
| American Board of Medical Specialties | society | 0.1288 | 9 | 9 |
| Harvey Cushing | person | 0.1036 | 12 | 12 |
| Michael DeBakey | person | 0.1005 | 14 | 14 |
| John L. Cameron | person | 0.0914 | 6 | 6 |
| David Sabiston | person | 0.0905 | 10 | 10 |
| ACS National Surgical Quality Improvement Program | institution | 0.0863 | 6 | 6 |
| Owen Wangensteen | person | 0.0762 | 10 | 10 |
| Society of American Gastrointestinal and Endoscopic Surgeons | society | 0.0678 | 10 | 10 |
| American Association for Thoracic Surgery | society | 0.0603 | 9 | 9 |
| Mayo Clinic Department of Surgery | institution | 0.0557 | 5 | 5 |
| American Society of Colon and Rectal Surgeons | society | 0.0501 | 4 | 4 |
| Evarts A. Graham | person | 0.0422 | 6 | 6 |
| American Board of Orthopaedic Surgery | society | 0.0421 | 2 | 2 |
| Barney Brooks | person | 0.0409 | 3 | 3 |
| American Orthopaedic Association | society | 0.0403 | 4 | 4 |
| Alton Ochsner | person | 0.0381 | 5 | 5 |
| LaSalle D. Leffall Jr. | person | 0.0371 | 5 | 5 |
| Society of Neurological Surgeons | society | 0.0363 | 4 | 4 |

### G_train (directed person↔person lineage projection) — top 25

| Node | Type | Betweenness | In | Out |
|---|---|---|---|---|
| Alfred Blalock | person | 0.0064 | 2 | 12 |
| William Stewart Halsted | person | 0.0049 | 1 | 10 |
| Barney Brooks | person | 0.0040 | 1 | 1 |
| Thomas Starzl | person | 0.0024 | 1 | 9 |
| Theodor Billroth | person | 0.0022 | 1 | 1 |
| Harvey Cushing | person | 0.0020 | 2 | 7 |
| Robert E. Gross | person | 0.0015 | 2 | 4 |
| David Sabiston | person | 0.0013 | 1 | 5 |
| John Homans | person | 0.0011 | 1 | 1 |
| Theodor Kocher | person | 0.0006 | 1 | 1 |
| John Kirklin | person | 0.0005 | 1 | 2 |
| Michael DeBakey | person | 0.0005 | 1 | 9 |
| Elliott Cutler | person | 0.0004 | 1 | 2 |
| Walter Dandy | person | 0.0004 | 1 | 1 |
| Mont Reid | person | 0.0004 | 1 | 2 |
| Owen Wangensteen | person | 0.0004 | 1 | 7 |
| John L. Cameron | person | 0.0003 | 2 | 1 |
| A. Earl Walker | person | 0.0003 | 1 | 1 |
| Denton Cooley | person | 0.0003 | 2 | 1 |
| W. Hardy Hendren III | person | 0.0003 | 1 | 1 |
| William Longmire | person | 0.0003 | 1 | 1 |
| Wilder Penfield | person | 0.0002 | 1 | 1 |
| E. Stanley Crawford | person | 0.0002 | 1 | 2 |
| Francis D. Moore | person | 0.0002 | 1 | 2 |
| H. Glenn Bell | person | 0.0002 | 1 | 1 |

### G_train_u (undirected person↔person lineage projection) — top 25

| Node | Type | Betweenness | In | Out |
|---|---|---|---|---|
| Alfred Blalock | person | 0.2007 | 14 | 14 |
| William Stewart Halsted | person | 0.1746 | 11 | 11 |
| Barney Brooks | person | 0.1367 | 2 | 2 |
| Harvey Cushing | person | 0.0761 | 9 | 9 |
| Denton Cooley | person | 0.0710 | 3 | 3 |
| Michael DeBakey | person | 0.0646 | 10 | 10 |
| Thomas Starzl | person | 0.0588 | 10 | 10 |
| John Homans | person | 0.0556 | 2 | 2 |
| Robert E. Gross | person | 0.0522 | 6 | 6 |
| David Sabiston | person | 0.0336 | 6 | 6 |
| Mont Reid | person | 0.0203 | 3 | 3 |
| E. Stanley Crawford | person | 0.0137 | 3 | 3 |
| Elliott Cutler | person | 0.0137 | 3 | 3 |
| John Kirklin | person | 0.0137 | 3 | 3 |
| John L. Cameron | person | 0.0137 | 3 | 3 |
| Walter Dandy | person | 0.0136 | 2 | 2 |
| A. Earl Walker | person | 0.0069 | 2 | 2 |
| H. Glenn Bell | person | 0.0069 | 2 | 2 |
| W. Hardy Hendren III | person | 0.0069 | 2 | 2 |
| Wilder Penfield | person | 0.0069 | 2 | 2 |
| William Longmire | person | 0.0069 | 2 | 2 |
| Theodor Billroth | person | 0.0057 | 2 | 2 |
| Owen Wangensteen | person | 0.0045 | 8 | 8 |
| Theodor Kocher | person | 0.0011 | 2 | 2 |
| C. Walton Lillehei | person | 0.0009 | 2 | 2 |

## 2 — Trunk roots (person↔person lineage projection)

`G_train` = training edges (`direct_training`, `observational_study`) with **both endpoints person**: 152 nodes / 134 edges.
Weakly-connected components: 23 total; 4 major (size ≥ 5, 4 components); 8 major trunk root(s) — all persons.

> **Definitional fix (V13-DIAG-FIX).** The prior run filtered on edge_type alone, pulling 12 non-person training edges into the projection (chiefly institution→person `direct_training`) and seating institutions (Mayo/JHH/Howard/MSK departments) as trunk roots. Restricting to person↔person yields the correct **138 nodes / 24 weak components / 5 components ≥ 5**, with all trunk roots persons. Excluded edges enumerated in the REVIEW section.

### Major trunk roots (components size ≥ threshold)

| Comp # | Size | Edges | Root(s) |
|---|---|---|---|
| 0 | 80 | 83 | Alton Ochsner, Bernhard von Langenbeck, George Zuidema, Helen Taussig, William E. Ladd |
| 1 | 12 | 12 | William J. Mayo |
| 2 | 5 | 4 | Edward P. Richardson |
| 3 | 5 | 4 | Vilray Blair |

### Full census (all components)

| Comp # | Size | Edges | Major | Root(s) |
|---|---|---|---|---|
| 0 | 80 | 83 | Y | Alton Ochsner, Bernhard von Langenbeck, George Zuidema, Helen Taussig, William E. Ladd |
| 1 | 12 | 12 | Y | William J. Mayo |
| 2 | 5 | 4 | Y | Edward P. Richardson |
| 3 | 5 | 4 | Y | Vilray Blair |
| 4 | 4 | 3 |  | Allen O. Whipple, Burke Syphax |
| 5 | 4 | 3 |  | I.S. Ravdin |
| 6 | 4 | 3 |  | John Najarian |
| 7 | 3 | 2 |  | C. Gardner Child III, Frederick Coller |
| 8 | 3 | 2 |  | Charles Frazier |
| 9 | 3 | 2 |  | John Hunter |
| 10 | 3 | 2 |  | Philippe Mouret |
| 11 | 3 | 2 |  | Rupert B. Turnbull |
| 12 | 3 | 2 |  | Willard E. Goodwin |
| 13 | 2 | 1 |  | Andrew Morrow |
| 14 | 2 | 1 |  | Arthur Blakemore |
| 15 | 2 | 1 |  | Charles Elsberg |
| 16 | 2 | 1 |  | Ernest Sachs |
| 17 | 2 | 1 |  | Evarts A. Graham |
| 18 | 2 | 1 |  | George Humphreys |
| 19 | 2 | 1 |  | George McClellan |
| 20 | 2 | 1 |  | Henry Harkins |
| 21 | 2 | 1 |  | John Charnley |
| 22 | 2 | 1 |  | Warren Cole |

## 3 — Root-to-root geodesics (undirected, full graph)

18 cross-trunk major-root pair(s). Unreachable: 0 (expected 0 given single component).

### Distance matrix

| | Alton Ochsner | Bernhard… | George Zuidema | Helen Taussig | William… | William… | Edward… | Vilray Blair |
|---|---|---|---|---|---|---|---|---|
| Alton Ochsner | · | — | — | — | — | 4 | 5 | 5 |
| Bernhard… | — | · | — | — | — | 6 | 8 | 7 |
| George Zuidema | — | — | · | — | — | 4 | 5 | 6 |
| Helen Taussig | — | — | — | · | — | 5 | 6 | 7 |
| William… | — | — | — | — | · | 4 | 6 | 8 |
| William… | 4 | 6 | 4 | 5 | 4 | · | 6 | 6 |
| Edward… | 5 | 8 | 5 | 6 | 6 | 6 | · | 8 |
| Vilray Blair | 5 | 7 | 6 | 7 | 8 | 6 | 8 | · |

### Per-pair geodesics

| A | B | Dist | Single-bridge | Path |
|---|---|---|---|---|
| Alton Ochsner | William J. Mayo | 4 |  | Alton Ochsner → American College of Surgeons → ACS National Surgical Quality Improvement Program → Mayo Clinic Department of Surgery → William J. Mayo |
| George Zuidema | William J. Mayo | 4 |  | George Zuidema → Johns Hopkins Hospital Department of Surgery → ACS National Surgical Quality Improvement Program → Mayo Clinic Department of Surgery → William J. Mayo |
| William E. Ladd | William J. Mayo | 4 |  | William E. Ladd → Robert E. Gross → John Kirklin → Mayo Clinic Department of Surgery → William J. Mayo |
| Alton Ochsner | Edward P. Richardson | 5 |  | Alton Ochsner → American College of Surgeons → Joseph E. Murray → Francis D. Moore → Edward Churchill → Edward P. Richardson |
| Alton Ochsner | Vilray Blair | 5 |  | Alton Ochsner → American College of Surgeons → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| George Zuidema | Edward P. Richardson | 5 |  | George Zuidema → John L. Cameron → Keith D. Lillemoe → Massachusetts General Hospital Department of Surgery → Edward Churchill → Edward P. Richardson |
| Helen Taussig | William J. Mayo | 5 |  | Helen Taussig → Alfred Blalock → Henry Bahnson → American Surgical Association → Owen Wangensteen → William J. Mayo |
| Bernhard von Langenbeck | William J. Mayo | 6 |  | Bernhard von Langenbeck → Theodor Billroth → William Stewart Halsted → Johns Hopkins Hospital Department of Surgery → ACS National Surgical Quality Improvement Program → Mayo Clinic Department of Surgery → William J. Mayo |
| George Zuidema | Vilray Blair | 6 |  | George Zuidema → John L. Cameron → American College of Surgeons → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| Helen Taussig | Edward P. Richardson | 6 |  | Helen Taussig → Alfred Blalock → John L. Cameron → Keith D. Lillemoe → Massachusetts General Hospital Department of Surgery → Edward Churchill → Edward P. Richardson |
| William E. Ladd | Edward P. Richardson | 6 |  | William E. Ladd → Robert E. Gross → American Pediatric Surgical Association → Patricia K. Donahoe → Massachusetts General Hospital Department of Surgery → Edward Churchill → Edward P. Richardson |
| William J. Mayo | Edward P. Richardson | 6 |  | William J. Mayo → Owen Wangensteen → American Surgical Association → Frederick Coller → Massachusetts General Hospital Department of Surgery → Edward Churchill → Edward P. Richardson |
| William J. Mayo | Vilray Blair | 6 |  | William J. Mayo → Owen Wangensteen → American Surgical Association → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| Bernhard von Langenbeck | Vilray Blair | 7 |  | Bernhard von Langenbeck → Theodor Billroth → William Stewart Halsted → Howard Naffziger → American Board of Neurological Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| Helen Taussig | Vilray Blair | 7 |  | Helen Taussig → Alfred Blalock → Denton Cooley → American College of Surgeons → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| Bernhard von Langenbeck | Edward P. Richardson | 8 |  | Bernhard von Langenbeck → Theodor Billroth → William Stewart Halsted → Johns Hopkins Hospital Department of Surgery → John L. Cameron → Keith D. Lillemoe → Massachusetts General Hospital Department of Surgery → Edward Churchill → Edward P. Richardson |
| Edward P. Richardson | Vilray Blair | 8 |  | Edward P. Richardson → Edward Churchill → Francis D. Moore → Murray F. Brennan → Society of Surgical Oncology → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| William E. Ladd | Vilray Blair | 8 |  | William E. Ladd → Robert E. Gross → John Kirklin → American Association for Thoracic Surgery → Evarts A. Graham → Washington University Department of Surgery → Washington University → Washington University Division of Plastic Surgery → Vilray Blair |

### Top bridge intermediaries (geodesic interior-node frequency)

| Node | Times on a geodesic |
|---|---|
| Edward Churchill | 7 |
| American Board of Medical Specialties | 6 |
| American Board of Plastic Surgery | 6 |
| American College of Surgeons | 5 |
| American Board of Surgery | 5 |
| Massachusetts General Hospital Department of Surgery | 5 |
| Mayo Clinic Department of Surgery | 4 |
| John L. Cameron | 4 |
| ACS National Surgical Quality Improvement Program | 3 |
| Theodor Billroth | 3 |
| William Stewart Halsted | 3 |
| Johns Hopkins Hospital Department of Surgery | 3 |
| Keith D. Lillemoe | 3 |
| Alfred Blalock | 3 |
| American Surgical Association | 3 |

## 4 — Floating-person recount (persons only)

Total persons: 223.

| Cut | Definition | Count |
|---|---|---|
| (a) full_degree1 | degree==1 in G_full_u | 60 (prior V11/V12 ~53) |
| (b) training_leaves | (in+out)≤1 in G_train | 174 |
|     ↳ training-isolated (deg 0) | no training edge at all | 71 |
|     ↳ training leaf (deg 1) | single training edge | 103 |
| (c) lineage_absent | 0 training edges, ≥1 non-training edge in G_full | 71 |

### Overlaps

- `full_degree1_AND_training_leaves`: 60
- `full_degree1_AND_lineage_absent`: 26
- `training_leaves_AND_lineage_absent`: 71

### Cut (c) lineage_absent — examples (in the atlas, in no lineage)

- Arpad G. Gerster
- Arthur H. Aufses Jr.
- Barbara Lee Bass
- C. William Schwab
- Carlos A. Pellegrini
- Charles Miller
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
- Frederick Salmon
- … (+51 more)

## Excluded non-person training edges (REVIEW)

12 training-type edge(s) (`direct_training` / `observational_study`) have a non-person endpoint and are therefore **excluded from the person↔person lineage projection**. `direct_training` is expected to run person↔person; institution-as-trainer is a data-model question flagged for adjudication — **not** edited or deleted here (out of scope).

Non-person sources appearing (institution/society as trainer): Johns Hopkins Hospital Department of Surgery (5), Jefferson Medical College Department of Surgery (1), Lahey Clinic (1), Massachusetts General Hospital Department of Surgery (1), Mayo Clinic Department of Surgery (1), Memorial Sloan Kettering Cancer Center (1), Mobile Army Surgical Hospital (MASH) System (1), St. Mark's Hospital for Fistula and Other Diseases of the Rectum (1).

| Source | Src type | Target | Tgt type | Edge type | Module |
|---|---|---|---|---|---|
| Jefferson Medical College Department of Surgery | institution | Chevalier Jackson | person | direct_training | 08_subspecialties.json |
| Johns Hopkins Hospital Department of Surgery | institution | Arthur Blakemore | person | direct_training | 01_halsted_core.json |
| Johns Hopkins Hospital Department of Surgery | institution | J. Deryl Hart | person | direct_training | 01_halsted_core.json |
| Johns Hopkins Hospital Department of Surgery | institution | Joseph Marshall Flint | person | direct_training | 02_general_surgery_spread.json |
| Johns Hopkins Hospital Department of Surgery | institution | Peter Safar | person | direct_training | 02_general_surgery_spread.json |
| Johns Hopkins Hospital Department of Surgery | institution | Warfield Firor | person | direct_training | 01_halsted_core.json |
| Lahey Clinic | institution | Victor W. Fazio | person | direct_training | 08_subspecialties.json |
| Massachusetts General Hospital Department of Surgery | institution | Frederick Coller | person | direct_training | 02_general_surgery_spread.json |
| Mayo Clinic Department of Surgery | institution | R. Lee Clark | person | direct_training | 07_oncology_trials.json |
| Memorial Sloan Kettering Cancer Center | institution | LaSalle D. Leffall Jr. | person | direct_training | 02_general_surgery_spread.json |
| Mobile Army Surgical Hospital (MASH) System | institution | Norman Rich | person | observational_study | 14_global_military.json |
| St. Mark's Hospital for Fistula and Other Diseases of the Rectum | institution | Joseph M. Mathews | person | observational_study | 08_subspecialties.json |

## Tests

| # | Test | Result | Detail |
|---|---|---|---|
| 1.G_train_all_persons | | **PASS** | every G_train node is a person |
| 2.G_train_138n_24wcc_5big | | **FAIL** | nodes=152 (exp 138); weak_components=23 (exp 24); comps>=5: 4 (exp 5) |
| 3.trunk_roots_persons_and_match_reference | | **FAIL** | major roots (8): ['Alton Ochsner', 'Bernhard von Langenbeck', 'Edward P. Richardson', 'George Zuidema', 'Helen Taussig', 'Vilray Blair', 'William E. Ladd', 'William J. Mayo']; all persons=True; matches reference 7-root set=False | missing=['Owen Wangensteen', 'Thomas Starzl'] extra=['Edward P. Richardson', 'George Zuidema', 'William J. Mayo'] |
| 4.JohnHunter_indeg0_Halsted_indeg_ge1 | | **PASS** | John Hunter training in-degree=0 (exp 0); Halsted in-degree=1 (exp ≥1) |
| 5.full_degree1_53_and_Gfull_top5_unchanged | | **FAIL** | full_degree1=60 (exp 53); G_full top-5=['American College of Surgeons', 'ACS National Surgical Quality Improvement Program', 'Johns Hopkins Hospital Department of Surgery', 'Alfred Blalock', 'LaSalle D. Leffall Jr.']; unchanged=False |
| 6.excluded_nonperson_training_eq_27 | | **FAIL** | excluded non-person training edges=12 (exp 27) |
| 7.canonical_sha_unchanged | | **PASS** | before=d13d038d8c3d… after=d13d038d8c3d… |
| S1.canonical_node_count_415 | | **FAIL** | nodes=428; raw_edges=561; simple_edges=558 (collapsed 3) |
| S2.G_full_u_single_component | | **PASS** | components=1 |
| S3.betweenness_finite_all_4_graphs | | **PASS** | all four graphs finite & full coverage |
| S4.major_root_pairs_finite_distance | | **PASS** | 18 cross-trunk pairs; unreachable=0 |

