# V16_b1 Diagnostic Audit
Generated: 2026-07-19T04:01:00Z
Graph state: 561 edges across 15 module files, 428 unique nodes, 1 connected component(s)

## Summary of findings
- **Audit 1 (Canonical Names):** 0 person pair(s), 72 institution pair(s), 3 society pair(s) flagged (institution pairs ≥ 0.95: 0; whitelisted: 1)
- **Audit 2 (Temporal):** 0 sentinel/out-of-range, 0 logical inversion(s), 11 same-year ranged edge(s), 0 round-year cluster(s) flagged
- **Audit 3 (Dedup):** 0 literal duplicate group(s), 3 multi-type pair(s), 0 multi-governance case(s) (overlapping: 0)

## Recommended next steps
- Zero blocking issues surfaced.

---

## Graph composition

### Module inventory
- `01_halsted_core.json`: 16 edges
- `02_general_surgery_spread.json`: 136 edges
- `03_neurosurgery.json`: 32 edges
- `04_cardiothoracic_vascular.json`: 44 edges
- `05_urology.json`: 12 edges
- `06_orthopedics.json`: 12 edges
- `07_oncology_trials.json`: 20 edges
- `08_subspecialties.json`: 75 edges
- `09_trauma_acute_infection.json`: 21 edges
- `10_quality_outcomes.json`: 21 edges
- `11_mis_robotic.json`: 15 edges
- `12_governance_societies.json`: 89 edges
- `13_pre_halsted.json`: 5 edges
- `14_global_military.json`: 14 edges
- `15_institutional_hierarchy.json`: 49 edges

### Edge-type distribution
- `governance_leadership`: 165
- `direct_training`: 136
- `institutional_founder`: 98
- `society_founder`: 62
- `institutional_parent`: 49
- `programmatic_accreditation`: 24
- `institutional_succession`: 18
- `observational_study`: 9

### Label file
- Total label entries: 428
- Stub entries pending adjudication: 100
- Reviewed / adjudicated entries: 328

---

## Audit 1 — Canonical Name Similarity

**Whitelisted (known-distinct, suppressed): 1 pair(s).**

- `ACS National Surgical Quality Improvement Program` ≈ `VA National Surgical Quality Improvement Program` (0.97) — distinct entities: VA NSQIP 1991–2001 (Khuri) vs ACS NSQIP 2004– (Ko/Flum); linked by an explicit institutional_succession edge

### Persons (0 pairs flagged)

_None flagged._

### Institutions (72 pairs flagged)

| Name A | Name B | Ratio | Modules A | Modules B | Note | Verdict |
|---|---|---|---|---|---|---|
| UAB Department of Surgery | UCLA Department of Surgery | 0.94 | 02 | 08 |  | MANUAL REVIEW |
| University of Pennsylvania Department of Neurosurgery | University of Pennsylvania Department of Surgery | 0.93 | 03, 15 | 02, 13, 15 |  | MANUAL REVIEW |
| Johns Hopkins Hospital Department of Neurosurgery | Johns Hopkins Hospital Department of Surgery | 0.92 | 03, 15 | 01, 02, 10, 12, 15 |  | MANUAL REVIEW |
| UCLA Department of Surgery | UCSF Department of Surgery | 0.92 | 08 | 02, 03 |  | MANUAL REVIEW |
| Washington University Department of Neurosurgery | Washington University Department of Surgery | 0.92 | 03, 15 | 02, 12, 15 |  | MANUAL REVIEW |
| Duke University Department of Surgery | Tulane University Department of Surgery | 0.92 | 02 | 04 |  | MANUAL REVIEW |
| Tulane University Department of Surgery | Yale University Department of Surgery | 0.92 | 04 | 02 |  | MANUAL REVIEW |
| Duke University Department of Surgery | Yale University Department of Surgery | 0.92 | 02 | 02 |  | MANUAL REVIEW |
| Emory University Department of Surgery | Howard University Department of Surgery | 0.91 | 02 | 02 |  | MANUAL REVIEW |
| Washington University Division of Plastic Surgery | Washington University Division of Urologic Surgery | 0.91 | 08, 15 | 05, 15 |  | MANUAL REVIEW |
| UAB Department of Surgery | UCSF Department of Surgery | 0.90 | 02 | 02, 03 |  | MANUAL REVIEW |
| Howard University Department of Surgery | Stanford University Department of Surgery | 0.90 | 02 | 02, 04 |  | MANUAL REVIEW |
| University of Miami Transplant Program | University of Minnesota Transplant Program | 0.90 | 02, 15 | 02, 15 |  | MANUAL REVIEW |
| University of Chicago Department of Surgery | University of Cincinnati Department of Surgery | 0.90 | 02 | 02 |  | MANUAL REVIEW |
| University of Chicago Department of Surgery | University of Washington Department of Surgery | 0.90 | 02 | 02, 09 |  | MANUAL REVIEW |
| Cornell University Department of Surgery | Emory University Department of Surgery | 0.90 | 02, 12 | 02 |  | MANUAL REVIEW |
| University of Chicago Department of Surgery | University of Colorado Department of Surgery | 0.90 | 02 | 02 |  | MANUAL REVIEW |
| University of Chicago Department of Surgery | University of Michigan Department of Surgery | 0.90 | 02 | 02 |  | MANUAL REVIEW |
| Howard University Department of Surgery | Yale University Department of Surgery | 0.89 | 02 | 02 |  | MANUAL REVIEW |
| Creighton University Department of Surgery | Washington University Department of Surgery | 0.89 | 02 | 02, 12, 15 |  | MANUAL REVIEW |
| Columbia University Department of Surgery | Cornell University Department of Surgery | 0.89 | 02 | 02, 12 |  | MANUAL REVIEW |
| University of Michigan Department of Surgery | University of Washington Department of Surgery | 0.89 | 02 | 02, 09 |  | MANUAL REVIEW |
| University of Pittsburgh Intestinal Transplant Program | University of Pittsburgh Transplant Program | 0.89 | 02, 15 | 02, 15 |  | MANUAL REVIEW |
| Cornell University Department of Surgery | Howard University Department of Surgery | 0.89 | 02, 12 | 02 |  | MANUAL REVIEW |
| Cornell University Department of Surgery | Tulane University Department of Surgery | 0.89 | 02, 12 | 04 |  | MANUAL REVIEW |
| Emory University Department of Surgery | Stanford University Department of Surgery | 0.89 | 02 | 02, 04 |  | MANUAL REVIEW |
| Fundamentals of Endoscopic Surgery | Fundamentals of Laparoscopic Surgery | 0.89 | 10 | 10 |  | MANUAL REVIEW |
| Cleveland Clinic Department of Colorectal Surgery | Cleveland Clinic Department of General Surgery | 0.88 | 08, 15 | 02, 15 |  | MANUAL REVIEW |
| Cornell University Department of Surgery | Duke University Department of Surgery | 0.88 | 02, 12 | 02 |  | MANUAL REVIEW |
| Cornell University Department of Surgery | Yale University Department of Surgery | 0.88 | 02, 12 | 02 |  | MANUAL REVIEW |
| Duke University Department of Surgery | Emory University Department of Surgery | 0.88 | 02 | 02 |  | MANUAL REVIEW |
| Emory University Department of Surgery | Yale University Department of Surgery | 0.88 | 02 | 02 |  | MANUAL REVIEW |
| University of Cincinnati Department of Surgery | University of Minnesota Department of Surgery | 0.88 | 02 | 12, 15 |  | MANUAL REVIEW |
| Cornell University Department of Surgery | Creighton University Department of Surgery | 0.88 | 02, 12 | 02 |  | MANUAL REVIEW |
| Tulane University Department of Surgery | Vanderbilt University Department of Surgery | 0.88 | 04 | 02 |  | MANUAL REVIEW |
| University of Michigan Department of Surgery | University of Minnesota Department of Surgery | 0.88 | 02 | 12, 15 |  | MANUAL REVIEW |
| Columbia University Department of Surgery | Howard University Department of Surgery | 0.88 | 02 | 02 |  | MANUAL REVIEW |
| Columbia University Department of Surgery | Tulane University Department of Surgery | 0.88 | 02 | 04 |  | MANUAL REVIEW |
| Ohio State University Department of Surgery | Yale University Department of Surgery | 0.88 | 02 | 02 |  | MANUAL REVIEW |
| Stanford University Department of Surgery | Tulane University Department of Surgery | 0.88 | 02, 04 | 04 |  | MANUAL REVIEW |
| Vanderbilt University Department of Surgery | Yale University Department of Surgery | 0.88 | 02 | 02 |  | MANUAL REVIEW |
| Columbia University Department of Surgery | East Carolina University Department of Surgery | 0.87 | 02 | 12, 15 |  | MANUAL REVIEW |
| Columbia University Department of Surgery | Duke University Department of Surgery | 0.87 | 02 | 02 |  | MANUAL REVIEW |
| Columbia University Department of Surgery | Yale University Department of Surgery | 0.87 | 02 | 02 |  | MANUAL REVIEW |
| Howard University Department of Surgery | Tulane University Department of Surgery | 0.87 | 02 | 04 |  | MANUAL REVIEW |
| Stanford University Department of Surgery | Yale University Department of Surgery | 0.87 | 02, 04 | 02 |  | MANUAL REVIEW |
| Duke University Department of Surgery | Howard University Department of Surgery | 0.87 | 02 | 02 |  | MANUAL REVIEW |
| Cornell University Department of Surgery | Stanford University Department of Surgery | 0.86 | 02, 12 | 02, 04 |  | MANUAL REVIEW |
| University of Chicago Department of Surgery | University of Minnesota Department of Surgery | 0.86 | 02 | 12, 15 |  | MANUAL REVIEW |
| Columbia University Department of Surgery | Emory University Department of Surgery | 0.86 | 02 | 02 |  | MANUAL REVIEW |
| Creighton University Department of Surgery | Duke University Department of Surgery | 0.86 | 02 | 02 |  | MANUAL REVIEW |
| Creighton University Department of Surgery | Yale University Department of Surgery | 0.86 | 02 | 02 |  | MANUAL REVIEW |
| University of Minnesota Department of Surgery | University of Pennsylvania Department of Surgery | 0.86 | 12, 15 | 02, 13, 15 |  | MANUAL REVIEW |
| Emory University Department of Surgery | Tulane University Department of Surgery | 0.86 | 02 | 04 |  | MANUAL REVIEW |
| Howard University Department of Surgery | Northwestern University Department of Surgery | 0.86 | 02 | 12, 15 |  | MANUAL REVIEW |
| Mayo Clinic Department of Orthopedic Surgery | Mayo Clinic Department of Surgery | 0.86 | 06, 15 | 02, 07, 10, 15 |  | MANUAL REVIEW |
| Ohio State University Department of Surgery | Stanford University Department of Surgery | 0.86 | 02 | 02, 04 |  | MANUAL REVIEW |
| Stanford University Department of Surgery | Vanderbilt University Department of Surgery | 0.86 | 02, 04 | 02 |  | MANUAL REVIEW |
| UC Davis Department of Surgery | UCLA Department of Surgery | 0.86 | 02, 12, 15 | 08 |  | MANUAL REVIEW |
| UC Davis Department of Surgery | UCSF Department of Surgery | 0.86 | 02, 12, 15 | 02, 03 |  | MANUAL REVIEW |
| University of Minnesota Department of Surgery | University of Washington Department of Surgery | 0.86 | 12, 15 | 02, 09 |  | MANUAL REVIEW |
| University of Colorado Department of Surgery | University of Minnesota Department of Surgery | 0.85 | 02 | 12, 15 |  | MANUAL REVIEW |
| Howard University Department of Surgery | Ohio State University Department of Surgery | 0.85 | 02 | 02 |  | MANUAL REVIEW |
| Howard University Department of Surgery | Vanderbilt University Department of Surgery | 0.85 | 02 | 02 |  | MANUAL REVIEW |
| Ohio State University Department of Surgery | Tulane University Department of Surgery | 0.85 | 02 | 04 |  | MANUAL REVIEW |
| Tulane University Department of Surgery | Washington University Department of Surgery | 0.85 | 04 | 02, 12, 15 |  | MANUAL REVIEW |
| University of Cincinnati Department of Surgery | University of Pennsylvania Department of Surgery | 0.85 | 02 | 02, 13, 15 |  | MANUAL REVIEW |
| Creighton University Department of Surgery | Northwestern University Department of Surgery | 0.85 | 02 | 12, 15 |  | MANUAL REVIEW |
| Creighton University Department of Surgery | Emory University Department of Surgery | 0.85 | 02 | 02 |  | MANUAL REVIEW |
| Duke University Department of Surgery | Ohio State University Department of Surgery | 0.85 | 02 | 02 |  | MANUAL REVIEW |
| Duke University Department of Surgery | Vanderbilt University Department of Surgery | 0.85 | 02 | 02 |  | MANUAL REVIEW |
| Washington University Department of Surgery | Yale University Department of Surgery | 0.85 | 02, 12, 15 | 02 |  | MANUAL REVIEW |

### Societies (3 pairs flagged)

| Name A | Name B | Ratio | Modules A | Modules B | Note | Verdict |
|---|---|---|---|---|---|---|
| American Association for the Surgery of Trauma | Eastern Association for the Surgery of Trauma | 0.90 | 09, 12 | 09 |  | MANUAL REVIEW |
| American Surgical Association | American Urological Association | 0.90 | 12, 13 | 05 |  | MANUAL REVIEW |
| American Society of Breast Surgeons | American Society of Transplant Surgeons | 0.89 | 07 | 02, 12 |  | MANUAL REVIEW |

---

## Audit 2 — Temporal Anomalies

### Sentinel / out-of-range values (0 edges)

_None flagged._

### Logical inversions (start > end, 0 edges)

_None flagged._

### Same-year edges on ranged types (11 edges — verify brief tenure vs data error)

| Module | Source | Target | Edge Type | Year |
|---|---|---|---|---|
| 02 | Thomas Starzl | Satoru Todo | direct_training | 1984 |
| 02 | Thomas Starzl | Kareem Abu-Elmagd | direct_training | 1989 |
| 02 | Thomas Starzl | Jorge Reyes | direct_training | 1988 |
| 02 | Thomas Starzl | Ron Shapiro | direct_training | 1988 |
| 02 | Satoru Todo | Hokkaido University | governance_leadership | 1997 |
| 02 | Kareem Abu-Elmagd | Cleveland Clinic | governance_leadership | 2015 |
| 02 | Velma Scantlebury | University of South Alabama | governance_leadership | 2002 |
| 02 | Jorge Reyes | University of Washington Department of Surgery | governance_leadership | 2004 |
| 02 | Ron Shapiro | Mount Sinai Hospital Recanati/Miller Transplantation Institute | governance_leadership | 2014 |
| 12 | Rudolph Matas | American Surgical Association | governance_leadership | 1909 |
| 12 | Goran Klintmalm | American Society of Transplant Surgeons | governance_leadership | 2005 |

### Round-year clusters (flag if >3% of total edges)

| Year | As start_year | As end_year | start % | end % | Flag |
|---|---|---|---|---|---|
| 1800 | 0 | 0 | 0.0% | 0.0% |  |
| 1850 | 0 | 0 | 0.0% | 0.0% |  |
| 1900 | 1 | 1 | 0.2% | 0.2% |  |
| 1950 | 3 | 7 | 0.5% | 1.2% |  |
| 2000 | 3 | 1 | 0.5% | 0.2% |  |

---

## Audit 3 — Dedup Discipline

### Check A — literal (source, target, edge_type) duplicates (0 groups)

_Expected: zero rows. Any rows = merge pipeline failure._

_No literal duplicates found._

### Check B — same source→target with multiple edge_types (3 pairs)

| Source | Target | Edge Types | Temporal Ranges | Modules | Review |
|---|---|---|---|---|---|
| J. Deryl Hart | Duke University Department of Surgery | governance_leadership; institutional_founder | 1930-1960 | 02 | MANUAL REVIEW |
| Joseph M. Mathews | American Proctologic Society | governance_leadership; society_founder | 1899; 1899-1901 | 08 | MANUAL REVIEW |
| Rudolph Matas | American College of Surgeons | governance_leadership; society_founder | 1913; 1925-1926 | 12 | MANUAL REVIEW |

### Check C — multi-governance_leadership to same institution (0 person↔institution pairs)

_None found._
