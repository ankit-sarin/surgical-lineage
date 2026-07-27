# NetworkX Structural Diagnostic — v17_b2 (interim)

Read-only analysis. Canonical sha256 `fb96a550dbab3e6aebb47f9e18f6568b0b355cc35f5b8bced7fbf5670b1f0c97` (unchanged after run: YES).
Graph: 450 nodes / 583 raw edges / 580 simple directed edges (3 parallel collapsed) / 5 component(s).
Parameters: threshold=5, top-n=25.

> Interim diagnostic on a still-growing graph — provisional numbers, not a manuscript lock.

## 1 — Betweenness centrality (normalized)

Full-graph tables annotate `node_type`: institution/society dominance is *why* manuscript lineage claims anchor on the training projection, not the full graph. `G_train` is the corrected **person↔person** lineage projection (both endpoints person); non-person training edges are excluded — see the REVIEW section.

### G_full (directed, all types) — top 25

| Node | Type | Betweenness | In | Out |
|---|---|---|---|---|
| American College of Surgeons | society | 0.0057 | 26 | 10 |
| ACS National Surgical Quality Improvement Program | institution | 0.0021 | 4 | 2 |
| Alfred Blalock | person | 0.0019 | 2 | 12 |
| Johns Hopkins Hospital Department of Surgery | institution | 0.0017 | 7 | 3 |
| William Stewart Halsted | person | 0.0013 | 1 | 11 |
| Barney Brooks | person | 0.0011 | 1 | 2 |
| Thomas Starzl | person | 0.0009 | 1 | 13 |
| American Board of Surgery | society | 0.0008 | 11 | 1 |
| Society of American Gastrointestinal and Endoscopic Surgeons | society | 0.0007 | 8 | 2 |
| Robert E. Gross | person | 0.0006 | 2 | 5 |
| Theodor Billroth | person | 0.0006 | 1 | 2 |
| American Society for Metabolic and Bariatric Surgery | society | 0.0006 | 2 | 1 |
| Peter Safar | person | 0.0006 | 1 | 2 |
| American Board of Medical Specialties | society | 0.0005 | 8 | 1 |
| Kathryn D. Anderson | person | 0.0005 | 1 | 3 |
| Harvey Cushing | person | 0.0005 | 2 | 10 |
| W. Hardy Hendren III | person | 0.0004 | 1 | 2 |
| David Sabiston | person | 0.0004 | 1 | 9 |
| John L. Cameron | person | 0.0004 | 2 | 4 |
| LaSalle D. Leffall Jr. | person | 0.0004 | 2 | 3 |
| Joseph E. Murray | person | 0.0004 | 1 | 2 |
| American Society for Bariatric Surgery | society | 0.0004 | 1 | 1 |
| American Surgical Association | society | 0.0004 | 18 | 1 |
| Francis D. Moore | person | 0.0003 | 1 | 3 |
| Mayo Clinic Department of Surgery | institution | 0.0003 | 4 | 1 |

### G_full_u (undirected, all types) — top 25

| Node | Type | Betweenness | In | Out |
|---|---|---|---|---|
| American College of Surgeons | society | 0.4216 | 36 | 36 |
| American Surgical Association | society | 0.2125 | 19 | 19 |
| William Stewart Halsted | person | 0.1524 | 12 | 12 |
| Alfred Blalock | person | 0.1466 | 14 | 14 |
| American Board of Surgery | society | 0.1396 | 12 | 12 |
| Thomas Starzl | person | 0.1242 | 14 | 14 |
| Johns Hopkins Hospital Department of Surgery | institution | 0.1223 | 10 | 10 |
| American Board of Medical Specialties | society | 0.1202 | 9 | 9 |
| Michael DeBakey | person | 0.0975 | 14 | 14 |
| Harvey Cushing | person | 0.0957 | 12 | 12 |
| David Sabiston | person | 0.0846 | 10 | 10 |
| John L. Cameron | person | 0.0823 | 6 | 6 |
| ACS National Surgical Quality Improvement Program | institution | 0.0765 | 6 | 6 |
| Owen Wangensteen | person | 0.0724 | 10 | 10 |
| Society of American Gastrointestinal and Endoscopic Surgeons | society | 0.0630 | 10 | 10 |
| American Association for Thoracic Surgery | society | 0.0568 | 9 | 9 |
| Mayo Clinic Department of Surgery | institution | 0.0509 | 5 | 5 |
| American Society of Colon and Rectal Surgeons | society | 0.0433 | 4 | 4 |
| University of Pennsylvania Department of Surgery | institution | 0.0433 | 7 | 7 |
| Allen O. Whipple | person | 0.0417 | 5 | 5 |
| American Board of Orthopaedic Surgery | society | 0.0395 | 2 | 2 |
| Evarts A. Graham | person | 0.0391 | 6 | 6 |
| Bernard Fisher | person | 0.0384 | 3 | 3 |
| American Orthopaedic Association | society | 0.0376 | 4 | 4 |
| Barney Brooks | person | 0.0371 | 3 | 3 |

### G_train (directed person↔person lineage projection) — top 25

| Node | Type | Betweenness | In | Out |
|---|---|---|---|---|
| Alfred Blalock | person | 0.0052 | 2 | 12 |
| William Stewart Halsted | person | 0.0040 | 1 | 10 |
| Barney Brooks | person | 0.0032 | 1 | 1 |
| Thomas Starzl | person | 0.0019 | 1 | 9 |
| Theodor Billroth | person | 0.0018 | 1 | 1 |
| Harvey Cushing | person | 0.0016 | 2 | 7 |
| Robert E. Gross | person | 0.0013 | 2 | 4 |
| David Sabiston | person | 0.0011 | 1 | 5 |
| John Homans | person | 0.0009 | 1 | 1 |
| Theodor Kocher | person | 0.0005 | 1 | 1 |
| John Kirklin | person | 0.0004 | 1 | 2 |
| Michael DeBakey | person | 0.0004 | 1 | 9 |
| Elliott Cutler | person | 0.0004 | 1 | 2 |
| Walter Dandy | person | 0.0004 | 1 | 1 |
| Mont Reid | person | 0.0003 | 1 | 2 |
| Owen Wangensteen | person | 0.0003 | 1 | 7 |
| John L. Cameron | person | 0.0003 | 2 | 1 |
| A. Earl Walker | person | 0.0002 | 1 | 1 |
| Denton Cooley | person | 0.0002 | 2 | 1 |
| W. Hardy Hendren III | person | 0.0002 | 1 | 1 |
| William Longmire | person | 0.0002 | 1 | 1 |
| Wilder Penfield | person | 0.0002 | 1 | 1 |
| E. Stanley Crawford | person | 0.0001 | 1 | 2 |
| Francis D. Moore | person | 0.0001 | 1 | 2 |
| H. Glenn Bell | person | 0.0001 | 1 | 1 |

### G_train_u (undirected person↔person lineage projection) — top 25

| Node | Type | Betweenness | In | Out |
|---|---|---|---|---|
| Alfred Blalock | person | 0.1640 | 14 | 14 |
| William Stewart Halsted | person | 0.1427 | 11 | 11 |
| Barney Brooks | person | 0.1117 | 2 | 2 |
| Harvey Cushing | person | 0.0622 | 9 | 9 |
| Denton Cooley | person | 0.0580 | 3 | 3 |
| Michael DeBakey | person | 0.0528 | 10 | 10 |
| Thomas Starzl | person | 0.0480 | 10 | 10 |
| John Homans | person | 0.0455 | 2 | 2 |
| Robert E. Gross | person | 0.0426 | 6 | 6 |
| David Sabiston | person | 0.0274 | 6 | 6 |
| Mont Reid | person | 0.0166 | 3 | 3 |
| E. Stanley Crawford | person | 0.0112 | 3 | 3 |
| Elliott Cutler | person | 0.0112 | 3 | 3 |
| John Kirklin | person | 0.0112 | 3 | 3 |
| John L. Cameron | person | 0.0112 | 3 | 3 |
| Walter Dandy | person | 0.0111 | 2 | 2 |
| A. Earl Walker | person | 0.0056 | 2 | 2 |
| H. Glenn Bell | person | 0.0056 | 2 | 2 |
| W. Hardy Hendren III | person | 0.0056 | 2 | 2 |
| Wilder Penfield | person | 0.0056 | 2 | 2 |
| William Longmire | person | 0.0056 | 2 | 2 |
| Theodor Billroth | person | 0.0047 | 2 | 2 |
| Owen Wangensteen | person | 0.0037 | 8 | 8 |
| Theodor Kocher | person | 0.0009 | 2 | 2 |
| C. Walton Lillehei | person | 0.0007 | 2 | 2 |

## 2 — Trunk roots (person↔person lineage projection)

`G_train` = training edges (`direct_training`, `observational_study`) with **both endpoints person**: 168 nodes / 146 edges.
Weakly-connected components: 27 total; 5 major (size ≥ 5, 5 components); 10 major trunk root(s) — all persons.

> **Definitional fix (V13-DIAG-FIX).** The prior run filtered on edge_type alone, pulling 3 non-person training edges into the projection (chiefly institution→person `direct_training`) and seating institutions (Mayo/JHH/Howard/MSK departments) as trunk roots. Restricting to person↔person yields the corrected projection reported directly above, with all trunk roots persons. (This note is deliberately count-free: it records a definitional fix, not a graph state, and its former hardcoded V13 counts went stale at every merge.) Excluded edges enumerated in the REVIEW section.

### Major trunk roots (components size ≥ threshold)

| Comp # | Size | Edges | Root(s) |
|---|---|---|---|
| 0 | 80 | 83 | Alton Ochsner, Bernhard von Langenbeck, George Zuidema, Helen Taussig, William E. Ladd |
| 1 | 12 | 12 | William J. Mayo |
| 2 | 6 | 5 | John Bell, John Hunter |
| 3 | 5 | 4 | Edward P. Richardson |
| 4 | 5 | 4 | Vilray Blair |

### Full census (all components)

| Comp # | Size | Edges | Major | Root(s) |
|---|---|---|---|---|
| 0 | 80 | 83 | Y | Alton Ochsner, Bernhard von Langenbeck, George Zuidema, Helen Taussig, William E. Ladd |
| 1 | 12 | 12 | Y | William J. Mayo |
| 2 | 6 | 5 | Y | John Bell, John Hunter |
| 3 | 5 | 4 | Y | Edward P. Richardson |
| 4 | 5 | 4 | Y | Vilray Blair |
| 5 | 4 | 3 |  | Allen O. Whipple, Burke Syphax |
| 6 | 4 | 3 |  | I.S. Ravdin |
| 7 | 4 | 3 |  | John Najarian |
| 8 | 4 | 3 |  | John Warren |
| 9 | 3 | 2 |  | Astley Cooper, Valentine Seaman |
| 10 | 3 | 2 |  | C. Gardner Child III, Frederick Coller |
| 11 | 3 | 2 |  | Charles Frazier |
| 12 | 3 | 2 |  | George McClellan, Joseph K. Swift |
| 13 | 3 | 2 |  | John Sheldon, Richard Bayley |
| 14 | 3 | 2 |  | Philippe Mouret |
| 15 | 3 | 2 |  | Rupert B. Turnbull |
| 16 | 3 | 2 |  | Willard E. Goodwin |
| 17 | 2 | 1 |  | Andrew Morrow |
| 18 | 2 | 1 |  | Arthur Blakemore |
| 19 | 2 | 1 |  | Carl W. Hughes |
| 20 | 2 | 1 |  | Charles Elsberg |
| 21 | 2 | 1 |  | Ernest Sachs |
| 22 | 2 | 1 |  | Evarts A. Graham |
| 23 | 2 | 1 |  | George Humphreys |
| 24 | 2 | 1 |  | Henry Harkins |
| 25 | 2 | 1 |  | John Charnley |
| 26 | 2 | 1 |  | Warren Cole |

## 3 — Root-to-root geodesics (undirected, full graph)

34 cross-trunk major-root pair(s). Unreachable: 0 (expected 0: all major roots lie in the giant component; the full graph has 5 component(s)).

### Distance matrix

| | Alton Ochsner | Bernhard… | George Zuidema | Helen Taussig | William… | William… | John Bell | John Hunter | Edward… | Vilray Blair |
|---|---|---|---|---|---|---|---|---|---|---|
| Alton Ochsner | · | — | — | — | — | 4 | 6 | 6 | 5 | 5 |
| Bernhard… | — | · | — | — | — | 6 | 9 | 9 | 8 | 7 |
| George Zuidema | — | — | · | — | — | 4 | 6 | 6 | 5 | 6 |
| Helen Taussig | — | — | — | · | — | 5 | 7 | 7 | 6 | 7 |
| William… | — | — | — | — | · | 4 | 9 | 9 | 6 | 8 |
| William… | 4 | 6 | 4 | 5 | 4 | · | 6 | 6 | 6 | 6 |
| John Bell | 6 | 9 | 6 | 7 | 9 | 6 | · | — | 8 | 8 |
| John Hunter | 6 | 9 | 6 | 7 | 9 | 6 | — | · | 8 | 8 |
| Edward… | 5 | 8 | 5 | 6 | 6 | 6 | 8 | 8 | · | 8 |
| Vilray Blair | 5 | 7 | 6 | 7 | 8 | 6 | 8 | 8 | 8 | · |

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
| Alton Ochsner | John Bell | 6 |  | Alton Ochsner → American College of Surgeons → Bernard Fisher → I.S. Ravdin → University of Pennsylvania Department of Surgery → William Gibson → John Bell |
| Alton Ochsner | John Hunter | 6 |  | Alton Ochsner → American College of Surgeons → Bernard Fisher → I.S. Ravdin → University of Pennsylvania Department of Surgery → Philip Syng Physick → John Hunter |
| Bernhard von Langenbeck | William J. Mayo | 6 |  | Bernhard von Langenbeck → Theodor Billroth → William Stewart Halsted → Johns Hopkins Hospital Department of Surgery → ACS National Surgical Quality Improvement Program → Mayo Clinic Department of Surgery → William J. Mayo |
| George Zuidema | John Bell | 6 |  | George Zuidema → John L. Cameron → American Surgical Association → Jonathan E. Rhoads → University of Pennsylvania Department of Surgery → William Gibson → John Bell |
| George Zuidema | John Hunter | 6 |  | George Zuidema → John L. Cameron → American Surgical Association → Jonathan E. Rhoads → University of Pennsylvania Department of Surgery → Philip Syng Physick → John Hunter |
| George Zuidema | Vilray Blair | 6 |  | George Zuidema → John L. Cameron → American Surgical Association → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| Helen Taussig | Edward P. Richardson | 6 |  | Helen Taussig → Alfred Blalock → John L. Cameron → Keith D. Lillemoe → Massachusetts General Hospital Department of Surgery → Edward Churchill → Edward P. Richardson |
| William E. Ladd | Edward P. Richardson | 6 |  | William E. Ladd → Robert E. Gross → American Pediatric Surgical Association → Patricia K. Donahoe → Massachusetts General Hospital Department of Surgery → Edward Churchill → Edward P. Richardson |
| William J. Mayo | Edward P. Richardson | 6 |  | William J. Mayo → Owen Wangensteen → American Surgical Association → Frederick Coller → Massachusetts General Hospital Department of Surgery → Edward Churchill → Edward P. Richardson |
| William J. Mayo | John Bell | 6 |  | William J. Mayo → Owen Wangensteen → American Surgical Association → Jonathan E. Rhoads → University of Pennsylvania Department of Surgery → William Gibson → John Bell |
| William J. Mayo | John Hunter | 6 |  | William J. Mayo → Owen Wangensteen → American Surgical Association → Jonathan E. Rhoads → University of Pennsylvania Department of Surgery → Philip Syng Physick → John Hunter |
| William J. Mayo | Vilray Blair | 6 |  | William J. Mayo → Owen Wangensteen → American Surgical Association → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| Bernhard von Langenbeck | Vilray Blair | 7 |  | Bernhard von Langenbeck → Theodor Billroth → William Stewart Halsted → Howard Naffziger → American Board of Neurological Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| Helen Taussig | John Bell | 7 |  | Helen Taussig → Alfred Blalock → Henry Bahnson → American Surgical Association → Jonathan E. Rhoads → University of Pennsylvania Department of Surgery → William Gibson → John Bell |
| Helen Taussig | John Hunter | 7 |  | Helen Taussig → Alfred Blalock → Henry Bahnson → American Surgical Association → Jonathan E. Rhoads → University of Pennsylvania Department of Surgery → Philip Syng Physick → John Hunter |
| Helen Taussig | Vilray Blair | 7 |  | Helen Taussig → Alfred Blalock → Denton Cooley → American College of Surgeons → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| Bernhard von Langenbeck | Edward P. Richardson | 8 |  | Bernhard von Langenbeck → Theodor Billroth → William Stewart Halsted → Johns Hopkins Hospital Department of Surgery → John L. Cameron → Keith D. Lillemoe → Massachusetts General Hospital Department of Surgery → Edward Churchill → Edward P. Richardson |
| Edward P. Richardson | Vilray Blair | 8 |  | Edward P. Richardson → Edward Churchill → Francis D. Moore → Murray F. Brennan → Society of Surgical Oncology → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| John Bell | Edward P. Richardson | 8 |  | John Bell → William Gibson → University of Pennsylvania Department of Surgery → Jonathan E. Rhoads → American Surgical Association → Frederick Coller → Massachusetts General Hospital Department of Surgery → Edward Churchill → Edward P. Richardson |
| John Bell | Vilray Blair | 8 |  | John Bell → William Gibson → University of Pennsylvania Department of Surgery → Jonathan E. Rhoads → American Surgical Association → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| John Hunter | Edward P. Richardson | 8 |  | John Hunter → Philip Syng Physick → University of Pennsylvania Department of Surgery → Jonathan E. Rhoads → American Surgical Association → Frederick Coller → Massachusetts General Hospital Department of Surgery → Edward Churchill → Edward P. Richardson |
| John Hunter | Vilray Blair | 8 |  | John Hunter → Philip Syng Physick → University of Pennsylvania Department of Surgery → Jonathan E. Rhoads → American Surgical Association → American Board of Surgery → American Board of Medical Specialties → American Board of Plastic Surgery → Vilray Blair |
| William E. Ladd | Vilray Blair | 8 |  | William E. Ladd → Robert E. Gross → John Kirklin → American Association for Thoracic Surgery → Evarts A. Graham → Washington University Department of Surgery → Washington University → Washington University Division of Plastic Surgery → Vilray Blair |
| Bernhard von Langenbeck | John Bell | 9 |  | Bernhard von Langenbeck → Theodor Billroth → William Stewart Halsted → Johns Hopkins Hospital Department of Surgery → John L. Cameron → American Surgical Association → Jonathan E. Rhoads → University of Pennsylvania Department of Surgery → William Gibson → John Bell |
| Bernhard von Langenbeck | John Hunter | 9 |  | Bernhard von Langenbeck → Theodor Billroth → William Stewart Halsted → Johns Hopkins Hospital Department of Surgery → John L. Cameron → American Surgical Association → Jonathan E. Rhoads → University of Pennsylvania Department of Surgery → Philip Syng Physick → John Hunter |
| William E. Ladd | John Bell | 9 |  | William E. Ladd → Boston Children's Hospital Department of Surgery → W. Hardy Hendren III → Kathryn D. Anderson → American College of Surgeons → Bernard Fisher → I.S. Ravdin → University of Pennsylvania Department of Surgery → William Gibson → John Bell |
| William E. Ladd | John Hunter | 9 |  | William E. Ladd → Boston Children's Hospital Department of Surgery → W. Hardy Hendren III → Kathryn D. Anderson → American College of Surgeons → Bernard Fisher → I.S. Ravdin → University of Pennsylvania Department of Surgery → Philip Syng Physick → John Hunter |

### Top bridge intermediaries (geodesic interior-node frequency)

| Node | Times on a geodesic |
|---|---|
| University of Pennsylvania Department of Surgery | 16 |
| American Surgical Association | 16 |
| Jonathan E. Rhoads | 12 |
| Edward Churchill | 9 |
| American College of Surgeons | 8 |
| William Gibson | 8 |
| Philip Syng Physick | 8 |
| American Board of Medical Specialties | 8 |
| American Board of Plastic Surgery | 8 |
| John L. Cameron | 8 |
| American Board of Surgery | 7 |
| Massachusetts General Hospital Department of Surgery | 7 |
| Theodor Billroth | 5 |
| William Stewart Halsted | 5 |
| Johns Hopkins Hospital Department of Surgery | 5 |

## 4 — Floating-person recount (persons only)

Total persons: 243.

| Cut | Definition | Count |
|---|---|---|
| (a) full_degree1 | degree==1 in G_full_u | 77 (baseline 61 at V16-B2; was ~53 through V11–V16-B1) |
| (b) training_leaves | (in+out)≤1 in G_train | 188 |
|     ↳ training-isolated (deg 0) | no training edge at all | 75 |
|     ↳ training leaf (deg 1) | single training edge | 113 |
| (c) lineage_absent | 0 training edges, ≥1 non-training edge in G_full | 75 |

### Overlaps

- `full_degree1_AND_training_leaves`: 77
- `full_degree1_AND_lineage_absent`: 35
- `training_leaves_AND_lineage_absent`: 75

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
- D. Hayes Agnew
- Dallas Phemister
- David Flum
- Dean DeWitt Lewis
- Diana Farmer
- Edward Delafield
- Eileen Bulger
- Ernest Codman
- Frank Lahey
- … (+55 more)

## Excluded non-person training edges (REVIEW)

3 training-type edge(s) (`direct_training` / `observational_study`) have a non-person endpoint and are therefore **excluded from the person↔person lineage projection**. `direct_training` is expected to run person↔person; institution-as-trainer is a data-model question flagged for adjudication — **not** edited or deleted here (out of scope).

Non-person sources appearing (institution/society as trainer): Johns Hopkins Hospital Department of Surgery (2), St. Mark's Hospital for Fistula and Other Diseases of the Rectum (1).

| Source | Src type | Target | Tgt type | Edge type | Module |
|---|---|---|---|---|---|
| Johns Hopkins Hospital Department of Surgery | institution | J. Deryl Hart | person | direct_training | 01_halsted_core.json |
| Johns Hopkins Hospital Department of Surgery | institution | Peter Safar | person | direct_training | 02_general_surgery_spread.json |
| St. Mark's Hospital for Fistula and Other Diseases of the Rectum | institution | Joseph McDowell Mathews | person | observational_study | 08_subspecialties.json |

## Tests

| # | Test | Result | Detail |
|---|---|---|---|
| 1.G_train_all_persons | | **PASS** | every G_train node is a person |
| 2.G_train_size_snapshot (info) | | **INFO** | G_train nodes=168; weak_components=27; components>=5: 5 |
| 3.trunk_roots_all_persons | | **PASS** | every major trunk root is a person |
| 3b.trunk_root_set_snapshot (info) | | **INFO** | major trunk roots (10): ['Alton Ochsner', 'Bernhard von Langenbeck', 'Edward P. Richardson', 'George Zuidema', 'Helen Taussig', 'John Bell', 'John Hunter', 'Vilray Blair', 'William E. Ladd', 'William J. Mayo'] |
| 4.JohnHunter_indeg0_Halsted_indeg_ge1 | | **PASS** | John Hunter training in-degree=0 (exp 0); Halsted in-degree=1 (exp ≥1) |
| 5.full_degree1_and_Gfull_top5_snapshot (info) | | **INFO** | full_degree1=77; G_full betweenness top-5=['American College of Surgeons', 'ACS National Surgical Quality Improvement Program', 'Alfred Blalock', 'Johns Hopkins Hospital Department of Surgery', 'William Stewart Halsted'] |
| 6.excluded_nonperson_training_snapshot (info) | | **INFO** | excluded non-person training edges=3 |
| 7.canonical_sha_unchanged | | **PASS** | before=fb96a550dbab… after=fb96a550dbab… |
| S1.node_and_edge_totals_snapshot (info) | | **INFO** | nodes=450; raw_edges=583; simple_edges=580 (collapsed 3) |
| S2.G_full_u_component_count (info) | | **INFO** | components=5; sizes=[440, 3, 3, 2, 2]; islands: 3n ['Gustaf Lindskog', 'Joseph Marshall Flint', 'Yale University Department of Surgery'] | 3n ['John Sheldon', 'Richard Bayley', 'Wright Post'] | 2n ['American Broncho-Esophagological Association', 'Chevalier Jackson'] | 2n ['Society of University Surgeons', 'Warfield Firor'] |
| S3.betweenness_finite_all_4_graphs | | **PASS** | all four graphs finite & full coverage |
| S4.major_root_pairs_finite_distance | | **PASS** | 34 cross-trunk pairs; unreachable=0 |

