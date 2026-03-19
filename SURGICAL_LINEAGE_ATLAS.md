# Surgical Lineage Atlas — Reference Document

## 1. Project Overview

The Surgical Lineage Atlas is a knowledge graph mapping the training lineages, institutional founding chains, governance networks, and programmatic accreditation relationships of American surgery. The graph spans 1777 (John Hunter training Henry Cline in London) through 2019 (ACS Geriatric Surgery Verification Program), with the primary American corpus beginning in 1805 (Physick's appointment as first professor of surgery at the University of Pennsylvania). The graph contains 382 edges connecting 318 nodes across three node types (person, institution, society) and seven edge types. Construction occurred in five build phases: the original build (source files 01–39, 196 edges) established the Halstedian lineage, major subspecialties, and governance structures; the gap closure phase (source files 40–54, 53 edges) extended the graph to independent non-Halstedian trunks, women in surgery, neurosurgery and urology expansion, the academic society pipeline, pre-Halsted Philadelphia surgery, and modern-era quality programs; the V3 expansion (8 expansion files, 6 upgrade manifests) added 27 edges and 16 citation upgrades covering kidney transplant origins, women's training lineages, URM depth, acute care surgery formalization, West Coast institutional depth, and MIS-governance bridging; the V4 expansion (7 update files) added 17 new edges, applied 7 PMID citation upgrades, corrected the Churchill training lineage, and bridged 4 disconnected components; the V5 expansion (25 expansion files from two planning sessions) added 65 new edges, 1 citation upgrade, and 2 PMID corrections, extending major training trees (Sabiston, Blalock, DeBakey, Wangensteen), adding institutional depth (UCSF, Stanford, Vanderbilt, Emory, Michigan, Hopkins modern succession), bridging 5 small-island components, and adding pre-Halsted and subspecialty lineages. A four-phase citation verification pipeline (Phase 1 existence, Phase 1.5 content-match, Phase 1.75 candidate search, Phase 2 adjudicated repair) replaced 52 incorrect PMIDs/DOIs, downgraded 32 unverifiable citations to institutional_archive, and deleted 4 unverifiable edges. The corpus was consolidated from 50 source files into 14 thematic modules on 2026-03-15, expanded to V3 and V4 on 2026-03-16, to V5 on 2026-03-17, citation-verified on 2026-03-17, and Phase 2.5 citation-upgraded on 2026-03-18.

## 2. Schema Reference

Based on JSON Schema draft-07 (`00_schema.json`).

### Edge Object Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_node` | string | yes | Name of the origin node |
| `source_node_type` | enum | yes | `person`, `institution`, or `society` |
| `target_node` | string | yes | Name of the destination node |
| `target_node_type` | enum | yes | `person`, `institution`, or `society` |
| `edge_type` | enum | yes | Relationship type (see below) |
| `start_year` | integer | yes | Year the relationship began |
| `end_year` | integer | yes | Year the relationship ended (null if ongoing) |
| `temporal_range` | string | yes | Human-readable date range (e.g., "1889-1922") |
| `evidence_citation` | string | yes | Citation identifier (PMID number, DOI, or archive name) |
| `evidence_type` | enum | yes | `PMID`, `DOI`, or `institutional_archive` |
| `evidence_locator` | string | yes | URL or archival path to the source |
| `confidence` | enum | yes | `high`, `moderate`, or `low` |
| `notes` | string | no | Research annotations and provenance context |

### Node Types

| Type | Description | Count |
|------|-------------|-------|
| `person` | Individual surgeons, physicians, scientists | 169 |
| `institution` | Departments of surgery, hospitals, research programs, clinics | 95 |
| `society` | Professional societies, certification boards, associations | 54 |

### Edge Types

| Type | Definition | Count |
|------|-----------|-------|
| `direct_training` | Formal residency or fellowship training relationship | 105 |
| `governance_leadership` | Served in a leadership role (president, chair, director) | 88 |
| `institutional_founder` | Founded or established an institution | 83 |
| `society_founder` | Founded a professional society or board | 54 |
| `programmatic_accreditation` | One organization accredits, oversees, or mandates another | 24 |
| `institutional_succession` | One institution evolved into or was replaced by another | 18 |
| `observational_study` | Observership, visiting scholar, or peer-to-peer knowledge exchange | 10 |

### Evidence Types

| Type | Description | Count |
|------|-------------|-------|
| `PMID` | PubMed-indexed publication | 204 |
| `institutional_archive` | Institutional archive, registry, or official history | 169 |
| `DOI` | Digital Object Identifier | 9 |

## 3. Module Index

| File | Thematic Scope | Edges | Key Figures / Institutions |
|------|---------------|------:|---------------------------|
| `01_halsted_core.json` | Halsted, his direct trainees, and Hopkins founding | 15 | Halsted, Cushing, Blalock, Young, Finney |
| `02_general_surgery_spread.json` | How Halstedian surgery spread to major US institutions | 100 | Wangensteen, Sabiston, Starzl, Kirklin, Najarian, Drew, Leffall, Howard, Churchill, Austen, MGH, Murray, Moore, Cole, Jonasson, Debas, Freischlag, Pellegrini, Flint, Richardson, Bollinger, Chitwood, Cox, Elkin, Scott, Rhoads, Zollinger, Silen, Mattox |
| `03_neurosurgery.json` | Cushing and downstream neurosurgical lineage and societies | 15 | Cushing, Dandy, Penfield, Semmes, AANS |
| `04_cardiothoracic_vascular.json` | Cardiac, thoracic, and vascular surgery | 28 | Graham, DeBakey, Shumway, SVS, AATS, Taussig, Morrow, Braunwald, Reemtsma, DeAnda |
| `05_urology.json` | Urology from independent NY trunk through Hopkins convergence | 9 | Guiteras, Young, Walsh, Clayman, AUA, ABU, Endourological Society |
| `06_orthopedics.json` | Orthopedic surgery — independent non-Halstedian trunk | 12 | Gibney, Campbell, Charnley, Coventry, HSS, AOA, AAOS, ABOS |
| `07_oncology_trials.json` | Clinical trials networks and surgical oncology | 20 | Fisher, NSABP, SWOG, NRG Oncology, GOG, SSO, Memorial Hospital, Brennan, ASBrS |
| `08_subspecialties.json` | Colorectal, pediatric, plastic, endocrine, HPB, bariatric, ENT, ophthalmology, hand | 58 | Blair, Brown, Ladd, Mason, Blumgart, IHPBA, AHPBA, ASCRS, ASMBS, Jackson, H. Martin, Delafield, Bunnell, Turnbull, Fazio, ABCRS, Fonkalsrud, Folkman, Hendren, Thompson, Nyhus, St. Mark's |
| `09_trauma_acute_infection.json` | Trauma systems, acute care surgery, surgical infection | 20 | Scudder, Altemeier, Schwab, SIS, EAST, AAST, ACS Fellowship, Mattox, Ben Taub |
| `10_quality_outcomes.json` | Quality improvement and outcomes science | 22 | Codman, NSQIP, ERAS, FLS, FES, GSV |
| `11_mis_robotic.json` | Minimally invasive and robotic surgery | 9 | Berci, Marks, Reddick, Marescaux, SAGES, Cedars-Sinai |
| `12_governance_societies.json` | Professional society governance, boards, academic pipeline | 57 | ACS, ASA, ABS, Jonasson, Zuidema, Leffall, Austen, Numann, AWS, ABO, ABMS, Murray, Debas, Ponsky, Phemister, Freischlag, Pellegrini, ABOHNS, Kocher |
| `13_pre_halsted.json` | Pre-Halstedian American surgery (1805–1884) | 5 | Physick, Gross, Hunter, Jefferson Medical College |
| `14_global_military.json` | European roots, Royal Colleges, military surgery | 12 | Hunter, Billroth, Langenbeck, Churchill, Rich, Bunnell, Kocher, Organ |
| **Total** | | **382** | |

## 4. Graph Architecture — Key Patterns

1. **Independent trunks.** The graph is not a single Halsted tree. Philadelphia (Physick 1805, Gross 1828), New York (Guiteras 1902), Columbia (Whipple 1921), orthopedics (Gibney/Campbell 1887–1909), Chicago (Phemister 1925), Penn (Ravdin 1945), and Michigan (Coller 1930) all represent independent or semi-independent surgical lineages. None of these founders were Halsted-trained.

2. **Generational society pattern: senior exclusive to younger inclusive.** Neurosurgery: SNS (1920, founding elite) followed by Harvey Cushing Society (1931, broader) followed by CNS (1951, open membership). Trauma: AAST (1938, senior) followed by EAST (1986, younger surgeons). Academic pipeline: ASA (senior) then SUS (mid-career, under 45) then AAS (junior, first 12 years of appointment). Each tier emerged because its predecessor was perceived as too exclusive.

3. **Society-to-board pattern.** Professional societies systematically spawned certification boards: AOA founded ABOS (1934), ACS and ASA co-founded ABS (1937), the Harvey Cushing Society catalyzed ABNS (1940), AUA organized ABU (1935). This pattern represents the formalization of specialty identity into credentialing authority.

4. **Convergence nodes.** NRG Oncology (2012) merged three independent trial networks: NSABP (Fisher/breast), GOG (Lewis/gynecologic), and RTOG (radiation). The AUA converged two independent origins: Guiteras' 1902 New York founding and Young's 1909 Hopkins presidency. Columbia Department of Surgery merged Whipple's independent trunk with Blakemore's Hopkins-trained lineage at a shared institutional node.

5. **Quality verification evolution.** The ACS drove successive verification programs across an expanding scope: COT trauma verification (1922), NSQIP outcomes measurement (2004), TQIP trauma quality (2008), MBSAQIP bariatric (2012), GSV geriatric (2019). A parallel chain ran through infection: SIS (1980) provided the science base for SIP (2002), which was superseded by SCIP (2006) under federal oversight.

6. **Bidirectional circuits.** Three instances of institutions training leaders who returned to lead them: Jefferson trained Gross, then Gross led Jefferson (1828/1856). UC Cincinnati trained Altemeier, then Altemeier led UC (1933/1952). Hopkins trained Cameron, then Cameron led Hopkins (1962/1984). These circuits represent closed loops in the directed graph.

7. **The Hopkins Invasion pattern.** Halsted trainees seeded surgery departments at distant institutions: Heuer to Cincinnati (1922), Hart to Duke (1930), Naffziger to UCSF (1929), Harkins to UW (1947), Holman to Stanford (1926). Each outpost then generated its own multi-generational successions. The pattern created a hub-and-spoke topology with Hopkins as the central node, detectable three and four generations downstream.

8. **MIS-to-certification bridge.** Before Priority 15, the MIS/endoscopic society cluster (SAGES and its founders) and the certification/governance cluster (ABS, ABMS, ACGME) were structurally disconnected. The SAGES to FLS to ABS pathway, created when ABS mandated FLS completion for board eligibility in 2009, is the only edge chain connecting these two clusters. It represents the first simulation-based assessment mandated for board certification in any surgical discipline. Note: SAGES was founded in 1981 by Gerald Marks (per PMID 29362909); Ponsky served as SAGES president 1990–91 (governance_leadership, not society_founder).

## 5. Gap Closure Log — Condensed

### Priority 1: Columbia / Whipple
**Edges added:** 3. Whipple founding Columbia Department of Surgery (1921), Whipple as ASA president (1939), Blakemore as Columbia governance leader (1940).
**Key finding:** Whipple was not Halsted-trained. Columbia represents an independent surgical trunk. Blakemore (Hopkins-trained, already in graph) bridges the two lineages at the shared Columbia node.
**New nodes:** Columbia University Department of Surgery.

### Priority 2: Orthopedic Expansion
**Edges added:** 5. Gibney founding AOA (1887), Campbell founding Campbell Clinic (1909) and AAOS (1933), AOA spawning both AAOS and ABOS.
**Key finding:** Orthopedic surgery has an entirely independent institutional trunk. The AOA (1887) predates the Halsted residency system. Campbell established the first orthopaedic residency (1924).
**New nodes:** Willis Campbell, Campbell Clinic, AOA, AAOS, ABOS.

### Priority 3: Neurosurgery Societies
**Edges added:** 4. Cushing founding SNS (1920) and Harvey Cushing Society (1931), Harvey Cushing Society succession to AANS (1967), Naffziger founding ABNS (1940).
**Key finding:** The three-tiered society structure (SNS/Harvey Cushing Society/CNS) established the generational exclusivity-to-inclusivity pattern repeated in trauma and academic surgery.
**New nodes:** SNS, Harvey Cushing Society, AANS, ABNS.

### Priority 4: AUA Founding
**Edges added:** 2. Guiteras founding AUA (1902), Young as AUA president (1909).
**Key finding:** The AUA has a dual origin — Guiteras' independent New York founding converged with the Hopkins trunk through Young's presidency. AUA eventually headquartered at Young's Baltimore estate.
**New nodes:** Ramon Guiteras, AUA.

### Priority 5: Halstedian Outposts (Chicago, Penn, Michigan)
**Edges added:** 5. Phemister founding UChicago Surgery (1925), Ravdin founding UPenn Surgery (1945), Ravdin training Fisher, Coller founding UMichigan Surgery (1930), Coller as ASA president (1943).
**Key finding:** None of these three chairmen were Halsted-trained, despite leading major departments. Ravdin's training of Fisher connects the Penn trunk to the NSABP clinical trials lineage — the program that overturned Halsted's own radical mastectomy.
**New nodes:** Phemister, Ravdin, Coller, UChicago/UPenn/UMichigan Departments of Surgery.

### Priority 6: Plastic Surgery — American Trunk
**Edges added:** 3. Blair founding WashU Plastic Surgery (1925), Blair founding ABPS (1937), Blair's observational study with Gillies during WWI (1917).
**Key finding:** Blair's WWI observational study with Gillies is a transatlantic bridge connecting the independent American and British plastic surgery lineages. Blair and Graham were WashU colleagues for decades, implicitly connecting plastic surgery to the cardiothoracic trunk.
**New nodes:** Vilray Blair, WashU Division of Plastic Surgery, ABPS.

### Priority 7: Women in Surgery
**Edges added:** 3. Jonasson as ACS Board of Regents member (1976) and ABS director (1980), Braunwald as AATS member (1963).
**Key finding:** Jonasson was the first woman on the ACS Board of Regents, first woman chief of surgery at a major hospital, and first woman chair of academic surgery at a coed institution. Braunwald performed the first open-heart surgery by a woman and designed the first successful artificial mitral valve.
**New nodes:** Olga Jonasson, Nina Starr Braunwald.

### Priority 8: Gynecologic Oncology
**Edges added:** 4. Lewis founding SGO (1969) and GOG (1970), GOG succession to NRG Oncology (2012), NSABP succession to NRG (2012).
**Key finding:** NRG Oncology is a convergence node where the gynecologic oncology trunk meets the Fisher/NSABP breast surgery lineage through a three-way merger (GOG + NSABP + RTOG).
**New nodes:** George C. Lewis Jr., SGO, GOG, NRG Oncology.

### Priority 9: Neurosurgery Expansion
**Edges added:** 4. Cushing training Penfield (1918) and Semmes (1908), Penfield founding Montreal Neurological Institute (1934), Semmes founding CNS (1951).
**Key finding:** Extended the neurosurgical lineage to the third generation. The Halsted to Cushing to Penfield to MNI chain is four generations deep — the longest unbroken person-to-institution lineage in the graph. MNI is the first Canadian institution.
**New nodes:** Wilder Penfield, Montreal Neurological Institute, R. Eustace Semmes, CNS.

### Priority 10: Urology Expansion
**Edges added:** 3. Walsh as Brady director (1974) and AUA leader (1982), AUA founding ABU (1934).
**Key finding:** Walsh (not Hopkins-trained — recruited externally from UCLA) bridges the founding era of urology to the modern era. The AUA to ABU edge follows the established society-to-board pattern.
**New nodes:** Patrick Walsh, ABU.

### Priority 11: Acute Care Surgery / EAST
**Edges added:** 4. Scudder founding ACS COT (1922), COT founding TQIP (2008), Schwab founding EAST (1986), EAST accreditation by AAST (1987).
**Key finding:** EAST's founding parallels the Harvey Cushing Society — both emerged because the senior society (AAST and SNS respectively) was too exclusive for younger surgeons. The COT node completes the trauma quality chain between ACS and TQIP.
**New nodes:** ACS Committee on Trauma, C. William Schwab, EAST.

### Priority 12: Surgical Infection Society
**Edges added:** 3. Reid training Altemeier (1933), Altemeier founding SIS (1980), SIS accrediting SIP (2002).
**Key finding:** Creates a three-generation Halstedian chain (Halsted to Reid to Altemeier to SIS) and closes the gap between the academic infection society and the federal quality initiatives (SIP to SCIP). The Cincinnati succession (Heuer to Reid to Altemeier) was known as the "Hopkins Invasion."
**New nodes:** William Altemeier, Surgical Infection Society.

### Priority 13: Academic Pipeline Societies (SUS / AAS)
**Edges added:** 4. Hopkins training Firor (1917), Firor founding SUS (1938), Zuidema as Hopkins surgeon-in-chief (1964), Zuidema founding AAS (1966).
**Key finding:** Firor was among the last surgeons trained within the original Halsted program. Zuidema succeeded Blalock, recruited Walsh and Cameron's generation, and founded the AAS — bridging the Halsted era to the modern Hopkins department. The AAS/SUS/ASA pipeline mirrors the CNS/AANS/SNS pattern.
**New nodes:** Warfield Firor, George Zuidema, SUS, AAS.

### Priority 14: Pre-Halsted American Surgery
**Edges added:** 3. Physick founding UPenn Surgery (1805), Jefferson training Gross (1826), Gross leading Jefferson (1856).
**Key finding:** Extended the graph's temporal range by 84 years. The Philadelphia trunk (Physick 1805 to UPenn; Gross 1828 to Jefferson to ASA) is the earliest documented American surgical lineage, operating independently for 84 years before Halsted's Baltimore program.
**New nodes:** Philip Syng Physick, Jefferson Medical College Department of Surgery.

### Priority 15: Modern Era (2000+)
**Edges added:** 3. SAGES founding FLS (2004), FLS mandated by ABS (2009), ACS founding GSV (2019).
**Key finding:** FLS to ABS is the only pathway connecting the MIS/endoscopic cluster to the certification/governance cluster. GSV (2019) is the most recent edge in the graph and the latest in the ACS quality verification evolution chain.
**New nodes:** Fundamentals of Laparoscopic Surgery, Geriatric Surgery Verification Program.

### Priority 16: Howard University / Black Surgical Lineage
**Edges added:** 6. Whipple training Drew at Columbia (1938), Drew as Howard surgery chairman (1941), Howard training Leffall (1948), MSK training Leffall (1957), Leffall as Howard surgery chairman (1970), Leffall as ACS president (1995).
**Key finding:** Creates the first African American surgical lineage in the graph, connecting the Columbia/Whipple trunk to an independent institutional lineage at Howard University. Charles R. Drew was trained by Whipple at Columbia (1938-1940), became the first African American ABS examiner (1941), and built the Howard surgery department until his death in 1950. LaSalle D. Leffall Jr. was Drew's student, trained at MSK (first Black fellow), returned to lead Howard for 25 years, and became the first African American president of the ACS (1995). The Drew→Leffall chain at Howard creates a bidirectional circuit (trained at Howard, then led Howard) paralleling the Gross→Jefferson and Altemeier→Cincinnati patterns. The MSK fellowship edge bridges the Howard trunk into the existing oncology cluster. The ACS presidency edge connects to the graph's highest-degree node (degree 23).
**New nodes:** Charles R. Drew, Howard University Department of Surgery, LaSalle D. Leffall Jr.

### Priority 17: Massachusetts General Hospital Department of Surgery
**Edges added:** 3. Churchill as MGH surgery chief (1931), Austen as MGH surgery chief (1969), Austen as ACS president (1992).
**Key finding:** Creates the MGH Department of Surgery institutional node, the most important surgical department not previously represented. Churchill (already in graph) designed the 'rectangular' residency model in 1938 — a deliberate departure from Halsted's pyramidal system that became the template for all modern US surgical training. Austen succeeded Churchill and held the position for 29 years, building MGH cardiac surgery and co-designing the cardiopulmonary bypass machine and intra-aortic balloon pump. The Halsted→Cushing→Churchill→MGH chain extends the Halstedian invasion to Boston.
**New nodes:** Massachusetts General Hospital Department of Surgery, W. Gerald Austen.

### Priority 18: Otolaryngology / Head and Neck Surgery
**Edges added:** 5. Jackson founding ABEA (1917), Triological Society founding ABOto (1924), Martin as Memorial Hospital H&N chief (1934), Martin founding SHNS (1954), SHNS merging into AHNS (1998).
**Key finding:** Fills the largest absent specialty. The ABOto (1924) is the second-oldest specialty board in the US, predating every surgical board in the graph. Jackson held the professorship of laryngology at Jefferson Medical College (existing node), creating an implicit connection to the pre-Halsted Philadelphia trunk. Martin was chief of the Head and Neck Service at Memorial Hospital (existing node), connecting the ENT cluster to the Whipple/oncology network. The SHNS→AHNS merger (1998) is a convergence node pattern paralleling NRG Oncology.
**New nodes:** Chevalier Jackson, American Broncho-Esophagological Association, Triological Society, American Board of Otolaryngology-Head and Neck Surgery, Hayes Martin, Society of Head and Neck Surgeons, American Head and Neck Society.

### Priority 19: Hand Surgery
**Edges added:** 2. Bunnell founding US Army Hand Surgery Centers (1944), Bunnell founding ASSH (1946).
**Key finding:** Documents the military-to-civilian creation of hand surgery as a specialty, paralleling the trauma (Scudder→COT) and MASH patterns. Bunnell's insight that hand surgery required multidisciplinary integration (orthopedics + plastic + general surgery) created the only major society spanning three parent specialties. ASSH's 35 founding members were drawn almost exclusively from the army hand centers.
**New nodes:** Sterling Bunnell, United States Army Hand Surgery Centers, American Society for Surgery of the Hand.

### Priority 20: Ophthalmology Origin
**Edges added:** 4. Delafield founding NY Eye Infirmary (1820), Delafield founding AOS (1864), AOS founding ABO (1916), ABO founding ABMS (1933).
**Key finding:** Documents the prototype for the society-to-board spawning pattern. The AOS (1864) is the oldest specialty medical society in the US. The ABO (1916) is the first specialty certifying board, predating all surgical boards by a decade+. The ABO→ABMS edge creates the ABMS convergence node for the entire board certification layer. The Delafield→NY Eye Infirmary edge (1820) is the earliest specialty institution founding in the graph.
**New nodes:** Edward Delafield, New York Eye Infirmary, American Ophthalmological Society, American Board of Ophthalmology, American Board of Medical Specialties.

### Priority 21: Yale University Department of Surgery
**Edges added:** 2. Flint founding Yale surgery department (1907), Lindskog as Yale surgery chair (1948).
**Key finding:** Flint (Hopkins MD 1900) established the Halsted residency model at Yale, making it one of the earliest Hopkins-model programs outside Baltimore. Lindskog administered the first human chemotherapy to a cancer patient in 1942 (nitrogen mustard for lymphosarcoma), launching the era of cancer chemotherapy. Yale is a marquee academic surgery department previously unrepresented.
**New nodes:** Joseph Marshall Flint, Yale University Department of Surgery, Gustaf Lindskog.

### Priority 22: Women in Surgery Expansion
**Edges added:** 3. Taussig collaborating with Blalock (1943), Numann founding AWS (1981), Numann as ABS chair (1994).
**Key finding:** Doubles the number of women person nodes from 2 to 4. Taussig's conceptual insight enabled the blue baby operation (already linked to Blalock, Cooley, and Longmire in the graph). Numann was the first woman ABS chair and founded the Association of Women Surgeons. Her ABS chairmanship connects the women-in-surgery cluster to the graph's core certification node.
**New nodes:** Helen Taussig, Patricia Numann, Association of Women Surgeons.

### Priority 23: ABMS Convergence
**Edges added:** 3. ABS→ABMS (1937), ABNS→ABMS (1940), ABOS→ABMS (1934).
**Key finding:** Connects three existing surgical board nodes to the ABMS umbrella node (created by Priority 20). This completes the governance convergence pattern: independent specialty lineages flow through their respective boards into a single accreditation umbrella. The orthopedic board connection (ABOS→ABMS) is structurally significant because it bridges the independent non-Halstedian orthopedics trunk into the same governance framework as the Halstedian surgical boards.
**New nodes:** None (ABMS created by Priority 20; all boards already exist).

## 6. Data Quality & Provenance

| Metric | Value |
|--------|-------|
| Total edges | 382 |
| Unique nodes | 318 |
| Persons | 169 |
| Institutions | 95 |
| Societies | 54 |
| Duplicate edges | 0 |
| Node-type inconsistencies | 0 |
| Edges backed by PMID | 204 (53.4%) |
| Edges backed by institutional_archive | 169 (44.2%) |
| Edges backed by DOI | 9 (2.4%) |
| Wikipedia citations | 0 (last one eliminated V3: Ravdin→Fisher) |
| Non-standard evidence_types normalized | 2 (journal_article and secondary_source in Ravdin edges, V2) |
| V3 expansion edges added | 27 (8 expansion files) |
| V3 citation upgrades applied | 16 (14 PMID + 2 DOI, from 6 manifests) |
| V4 expansion edges added | 17 (5 expansion files) |
| V4 citation upgrades applied | 7 PMID (from 1 manifest, 3 entries marked KEEP_ARCHIVE) |
| V4 corrections applied | 3 (1 edge replacement, 1 notes correction, 1 temporal correction) |
| V5 expansion edges added | 65 (25 expansion files from 2 planning sessions) |
| V5 citation upgrades applied | 1 (Holman→Stanford PMID upgrade) |
| V5 PMID corrections | 2 (18294269→DOI, 33421312→DOI) |
| V5 cross-module duplicate removed | 1 (Cushing→Elkin in 03_neurosurgery) |
| PMID upgrade manifest entries | 44 total: 38 applied, 5 marked KEEP_ARCHIVE, 4 already had PMIDs |
| Connected components | 3 (down from 10 in V4, bridged by V5 small-islands batch) |
| Phase 2 citation repairs | 52 replaced, 32 archived, 4 deleted, 23 kept |
| Re-verification passes | 52/52 (100%) |
| Phase 2.5 PMID upgrades | 34 applied, 1 reverted (Blakemore) |
| Phase 2.5 verification flags resolved | 9 (8 cleared, 1 reverted) |
| Phase 2.5 structural corrections | 1 (Ponsky→SAGES reclassified; Marks→SAGES created) |
| Confidence distribution | High: 325; Moderate: 53; Low: 3 |
| Temporal range | 1777–2026 (start_year), primary American corpus 1805–2026 |

All person names, institution names, and society names are stored as full canonical strings (e.g., "William Stewart Halsted", not "Halsted"). No abbreviations are used in node names. Evidence locators include direct URLs to PubMed, DOI resolvers, or institutional web pages where available.

## 7. Reorganization Record

On 2026-03-15, 53 source files (50 edge files plus 3 special files) were consolidated into 14 thematic module files plus 4 supporting files (schema, PMID upgrade manifest, canonical flat file, README), totaling 18 output files. The output resides in the `consolidated/` directory.

The sorting logic used subspecialty-first classification: each edge was assigned to the most specific applicable module based on its primary subject matter. Cross-cutting edges (e.g., a person trained in one field who governed a society in another) were placed according to 19 explicit edge-case assignments documented in the `EXPLICIT_ASSIGNMENTS` dictionary within the script. Examples: Blalock training Cooley is a training edge assigned to general_surgery_spread (module 02), while Cooley training Frazier is assigned to cardiothoracic_vascular (module 04). Cushing training Churchill is assigned to general_surgery_spread because Churchill became a general surgery chief, not a neurosurgeon.

The execution script is `reorganize_graph.py`. It reads all source files, applies graph_update_draft removals and additions, normalizes evidence types, applies PMID upgrades from the manifest, classifies edges into modules, validates integrity (no duplicates, correct total count, schema compliance), and writes all output files. The script supports a `--dump` flag for diagnostic inspection of module assignments.

The file `surgical_lineage_graph_canonical.json` is the flat build artifact consumed by the D3 visualization layer. It contains all 382 edges sorted by `start_year` ascending (with `source_node` alphabetical as tiebreaker), each annotated with a `module` field indicating its thematic module assignment.

## 8. How to Expand the Graph

1. Identify the thematic module where the new edge(s) belong by reviewing the Module Index (Section 3) and the sorting rules in `reorganize_graph.py`.
2. Draft edge objects conforming to `00_schema.json`. All 12 required fields must be present. Use full canonical names for all nodes. Include a `notes` field with research provenance.
3. Append the new edge objects to the appropriate module JSON file in `consolidated/`. Maintain `start_year` ascending sort order within the file.
4. Regenerate `surgical_lineage_graph_canonical.json` by concatenating all 14 module files, adding a `module` field to each edge, and sorting by `start_year` ascending.
5. Validate: no duplicate `(source_node, target_node, edge_type)` triples across any module; all `evidence_type` values in the schema enum (`PMID`, `DOI`, `institutional_archive`); all required fields present; total edge count matches expected.
6. Update this reference document: revise the Module Index edge counts, add a changelog entry, and if applicable, add a Gap Closure Log entry for the new edges.
7. If the expansion involves PMID upgrades to existing edges, document the changes in `99_pmid_upgrade_manifest.json` with `source_node`, `target_node`, `edge_type`, `current_citation`, and upgrade fields.

## 9. V3 Expansion Changelog (2026-03-16)

### Summary

V3 integrated 27 new edges (8 expansion files) and 16 citation upgrades (6 upgrade manifests) from a gap analysis session targeting 14 structural priorities. The graph grew from 277 edges / 253 nodes (V2) to 304 edges / 273 nodes (V3). PMID-backed edges increased from 138 to 152 (50.0% of all edges). DOI-backed edges increased from 2 to 4. The sole Wikipedia citation in the graph (Ravdin→Fisher) was eliminated.

### Expansion Files (27 new edges)

| File | Edges | Target Modules | Key Content |
|------|------:|----------------|-------------|
| `expansion_A1_orthopedics_depth.json` | 5 | 06_orthopedics | HSS succession, Charnley/Wrightington, Coventry/Mayo hip arthroplasty |
| `expansion_A2_urology_modern.json` | 3 | 05_urology | Walsh/UCLA training, Clayman/WashU endourology, Endourological Society |
| `expansion_A3_1990s_temporal.json` | 4 | 07, 08 | SSO→ABS accreditation, Memorial→SSO founding, IHPBA→AHPBA, Blumgart→IHPBA |
| `expansion_A4_west_coast.json` | 3 | 02, 04, 12 | Debas/UCSF, Shumway/Stanford, Debas→ASA |
| `expansion_A5_women_urm.json` | 4 | 02, 04 | Cole→Jonasson, Jonasson→OSU, Drew→Leffall, Morrow→Braunwald |
| `expansion_A6_mis_training.json` | 2 | 11, 12 | Berci→Cedars-Sinai, Ponsky→ABS |
| `expansion_A7_transplant_murray.json` | 3 | 02, 12 | Murray→Brigham Transplant, Moore→Brigham Surgery, Murray→ACS |
| `expansion_A8_acute_care.json` | 3 | 09 | AAST→ACS Fellowship, Schwab→Penn Trauma, Schwab→AAST |

### Upgrade Manifests (16 citation upgrades)

| File | Upgrades | Type | Target Module |
|------|:--------:|------|---------------|
| `upgrade_B4_fisher_citation.json` | 1 | PMID | 07_oncology_trials |
| `upgrade_B1_trauma_citations.json` | 3 | PMID | 09_trauma_acute_infection |
| `upgrade_B2_quality_citations.json` | 3 | PMID | 10_quality_outcomes |
| `upgrade_B3_governance_citations.json` | 4 | 2 PMID + 2 DOI | 12_governance_societies |
| `upgrade_B5_general_surgery_spread_citations.json` | 3 | PMID | 02_general_surgery_spread |
| `upgrade_B6_subspecialties_citations.json` | 2 | PMID | 08_subspecialties |

### New Nodes (20)

**Persons (8):** Joseph E. Murray, Francis D. Moore, Warren Cole, Andrew Morrow, Haile T. Debas, Ralph V. Clayman, John Charnley, Mark B. Coventry

**Institutions (10):** Hospital for Special Surgery, Wrightington Centre for Hip Surgery, Mayo Clinic Department of Orthopedic Surgery, Washington University Division of Urologic Surgery, Peter Bent Brigham Hospital Renal Transplant Program, Peter Bent Brigham Hospital Department of Surgery, Ohio State University Department of Surgery, Cedars-Sinai Surgical Endoscopy Program, Acute Care Surgery Fellowship Program, Penn Trauma and Surgical Critical Care Fellowship

**Societies (2):** Endourological Society, Americas Hepato-Pancreato-Biliary Association

### Structural Impact

1. **Kidney transplant origin.** Murray→Brigham Renal Transplant Program (1954) and Moore→Brigham Department of Surgery (1948) add the origin of all organ transplantation, previously the largest missing institutional lineage.
2. **Women's training lineages.** Cole→Jonasson and Morrow→Braunwald are the first direct_training edges involving women in the graph, connecting governance-only nodes to the training backbone.
3. **Three-generation URM lineage.** Drew→Leffall creates the chain Whipple→Drew→Leffall, the longest URM lineage in the graph.
4. **Acute care surgery formalization.** AAST→ACS Fellowship (2008) transforms the AAST into a programmatic accreditor, paralleling ABS→ABMS.
5. **West Coast institutional depth.** Debas/UCSF and Shumway/Stanford add post-1960s edges to previously thin West Coast nodes.
6. **MIS-governance bridge.** Ponsky→ABS connects the MIS module to the certification backbone through a second pathway (complementing FLS→ABS).
7. **Orthopedic arthroplasty revolution.** Charnley→Coventry→Mayo creates a transatlantic knowledge bridge paralleling Blair→Gillies in plastic surgery.
8. **Endourology trunk.** Clayman/WashU and the Endourological Society create an independent urology lineage parallel to the Hopkins/Brady trunk.

### Flags for Manual Review

1. ~~**Cushing→Churchill edge** (02_general_surgery_spread): Churchill trained at MGH under Edward P. Richardson, not directly under Cushing at Brigham. Source_node may need revision.~~ **RESOLVED in V4:** Edge replaced with Richardson→Churchill. Notes corrected.
2. ~~**Kathryn Anderson and Julie Freischlag:** Ghost nodes appearing in notes fields with zero edges. Investigate whether edges should be created or notes cleaned.~~ **PARTIALLY RESOLVED in V4:** Freischlag now has 2 real edges (Hopkins governance, ACS presidency). Kathryn Anderson remains a ghost node.
3. ~~**Mason→Wangensteen training edge:** Confirmed (PhD 1953, Minnesota) but not included in V3. Consider adding in future update.~~ **RESOLVED in V4:** Temporal range corrected to 1945-1953 (edge already existed; dates were wrong).

## 10. V4 Expansion Changelog (2026-03-16)

### Summary

V4 integrated 17 new edges (5 expansion files), 7 PMID citation upgrades (1 upgrade manifest), and 3 corrections (1 audit file) from a gap analysis session targeting colorectal lineage, component bridging, women in surgery, West Coast depth, modern credentialing, and a historical error correction. The graph grew from 304 edges / 273 nodes (V3) to 321 edges / 282 nodes (V4). PMID-backed edges increased from 152 to 168 (52.3% of all edges). Connected components decreased from 14 to 10.

### Update Files

| File | Type | Changes | Key Content |
|------|------|--------:|-------------|
| `expansion_V4_01_colorectal.json` | Expansion | 6 edges | Colorectal surgery lineage: APS→ABCRS, ABCRS→ABMS, Turnbull→Cleveland Clinic CRS, Turnbull→Fazio, Fazio→Cleveland Clinic CRS, Fazio→ASCRS |
| `expansion_V4_02_bridges.json` | Expansion | 4 edges | Component bridging: Phemister→ASA, Hopkins→Flint, Blumgart→MSK, Brigham Dept→Brigham Transplant |
| `upgrade_V4_03_governance.json` | Upgrade | 7 PMID upgrades | Governance citations: Martin, Cameron (x2), ASA→ABS, Sabiston, Coller, Zuidema |
| `expansion_V4_05_women_urm.json` | Expansion | 2 edges | Freischlag as Hopkins surgeon-in-chief and ACS president |
| `expansion_V4_06_westcoast.json` | Expansion | 3 edges | Pellegrini at UW, Pellegrini→ASA, Longmire→Fonkalsrud |
| `audit_V4_07_churchill.json` | Audit | 3 corrections | Churchill training correction (Richardson replaces Cushing), notes fix, Mason temporal fix |
| `expansion_V4_08_modern.json` | Expansion | 2 edges | FES program: SAGES→FES, FES→ABS mandate |

### New Nodes (9)

**Persons (5):** Edward P. Richardson, Rupert B. Turnbull, Victor W. Fazio, Julie Ann Freischlag, Carlos A. Pellegrini, Eric W. Fonkalsrud

**Institutions (3):** Cleveland Clinic Department of Colorectal Surgery, Fundamentals of Endoscopic Surgery

**Societies (1):** American Board of Colon and Rectal Surgery

### Structural Impact

1. **Churchill correction.** The incorrect Cushing→Churchill direct_training edge has been replaced with Richardson→Churchill. Churchill trained at MGH under Edward P. Richardson, not under Cushing at Peter Bent Brigham Hospital. This breaks the Halsted→Cushing→Churchill→MGH chain, creating an independent Harvard/MGH surgical trunk parallel to the Hopkins/Halsted trunk.
2. **Component bridging (4 bridges).** Phemister→ASA connects the UChicago 2-node island. Hopkins→Flint connects the Yale 3-node island. Blumgart→MSK connects the HPB 6-node island. Brigham Dept→Brigham Transplant connects the Moore/Brigham 2-node island. Connected components reduced from 14 to 10.
3. **Colorectal surgery lineage.** Six edges create a complete colorectal subspecialty chain: APS→ABCRS (board founding), ABCRS→ABMS (board recognition), Turnbull→Cleveland Clinic CRS→Fazio→ASCRS. This is the first multi-generational colorectal lineage in the graph.
4. **FES chain.** SAGES→FES→ABS parallels the existing SAGES→FLS→ABS chain, documenting the second simulation-based assessment mandated for board certification.
5. **West Coast depth.** Pellegrini extends the UW succession chain (Harkins→Merendino→Pellegrini). Fonkalsrud extends the Blalock→Longmire→UCLA chain to a third generation.
6. **Freischlag.** First woman Hopkins surgeon-in-chief and ACS president. Converts a ghost node to a real person node with 2 edges.

### Flags for Manual Review

1. **Fazio→ASCRS edge** (08_subspecialties): evidence_type is institutional_archive. Notes say "CANDIDATE FOR PMID UPGRADE: search for Fazio ASCRS presidential address in Dis Colon Rectum 1996."
2. **Freischlag→ACS edge** (12_governance_societies): evidence_type is institutional_archive. Notes say "CANDIDATE FOR PMID UPGRADE: search for Freischlag ACS presidential address in Bull Am Coll Surg or JACS 2018-2019."
3. **Pellegrini→UW Dept edge** (02_general_surgery_spread): evidence_type is institutional_archive. Notes say "CANDIDATE FOR PMID UPGRADE: search for Pellegrini ASA presidential address in Ann Surg 2005-2006."
4. **Pellegrini→ASA edge** (12_governance_societies): evidence_type is institutional_archive. Same PMID upgrade candidate as above.
5. **Phemister→ASA edge** (12_governance_societies): evidence_type is institutional_archive. Notes say "CANDIDATE FOR PMID UPGRADE: search for Phemister ASA presidential address in Ann Surg 1938-1939."
6. **Longmire→Fonkalsrud edge** (08_subspecialties): evidence_type is institutional_archive. Notes say "CANDIDATE FOR PMID UPGRADE: search for Fonkalsrud obituary or tribute in J Pediatr Surg or Ann Surg 2017-2018."
7. **Sabiston→ACS PMID upgrade**: Confidence is moderate — the applied PMID (356789) documents Sabiston's ASA presidential address, not his ACS presidency specifically.
8. **Hopkins→Flint bridge edge**: Confidence is moderate — Flint received his Hopkins MD during the Halsted era but was primarily trained as an anatomist rather than as a Halsted surgical resident.
9. **Kathryn Anderson**: Remains a ghost node appearing in notes fields with zero edges. Investigate whether edges should be created or notes cleaned.

## 11. V5 Expansion Changelog (2026-03-17)

### Summary

V5 integrated 65 new edges (25 expansion files from two planning sessions), 1 citation upgrade (Holman→Stanford), and 2 PMID corrections. The graph grew from 321 edges / 282 nodes (V4) to 385 edges / 319 nodes (V5 pre-verification). One pre-existing cross-module duplicate (Cushing→Elkin) was removed. Connected components decreased from 10 to 3. A four-phase citation verification pipeline (Phase 1 existence, Phase 1.5 content-match, Phase 1.75 candidate search, Phase 2 adjudicated repair) then replaced 52 incorrect PMIDs/DOIs with verified candidates, downgraded 32 unverifiable citations to institutional_archive, and deleted 4 unverifiable edges, bringing the graph to 381 edges / 317 nodes (V5 post-verification). All 52 replacement citations passed re-verification.

### Expansion Files (65 new edges)

| File | Edges | Target Modules | Key Content |
|------|------:|----------------|-------------|
| `expansion_V5_T1-01_sabiston_training_tree.json` | 8 (5 post-Phase 2) | 02 | Sabiston trainees: Wolfe, Bollinger, Anderson, Chitwood, Cox, Spray, Jones; Anderson→Duke governance. Phase 2 deleted 3 unverifiable edges: Sabiston→Wolfe, Sabiston→Anderson, Sabiston→Spray |
| `expansion_V5_T1-02_blalock_training_tree.json` | 7 | 02, 04 | Blalock trainees: Haller, Hanlon, Jude, Muller, Ravitch, Scott, Longmire |
| `expansion_V5_T1-03_plastic_surgery_bridge.json` | 3 | 08 | Blair→Brown, Brown→Barrett, Barrett→ABPS bridge |
| `expansion_V5_T1-06_hunter_physick_bridge.json` | 1 | 13 | Hunter→Physick pre-Halsted bridge |
| `expansion_V5_T1-07_small_islands_batch.json` | 5 | 07, 08, 12 | 5 component bridges (Jackson/ABEA, ABOHNS/ABMS, Thompson/Michigan, ASBrS/ACS, St. Mark's/ASCRS) |
| `expansion_V5_T2-01_debakey_training_tree.json` | 6 | 02, 04 | DeBakey trainees: Crawford, Noon, Mattox, Morris, Garrett, Creech |
| `expansion_V5_T2-02_wangensteen_training_tree.json` | 4 | 02, 04 | Wangensteen trainees: Lillehei, Lewis, Merendino, Varco, Buchwald, Shumway, Mason |
| `expansion_V5_T2-03_rhoads_penn_lineage.json` | 3 | 02 | Rhoads/Penn lineage and governance |
| `expansion_V5_T2-04_zollinger_ohio_state.json` | 2 | 02 | Zollinger/Ohio State lineage |
| `expansion_V5_T2-05_brennan_msk.json` | 3 | 07 | Brennan MSK succession and cancer research |
| `expansion_V5_T2-06_ravitch_stapler.json` | 2 | 02 | Ravitch training and stapler innovation |
| `expansion_V5_T2-07_reemtsma_columbia.json` | 2 | 04 | Reemtsma/Columbia cardiothoracic lineage |
| `expansion_V5_T2-08_folkman_angiogenesis.json` | 2 | 08 | Gross→Folkman, Folkman→Boston Children's |
| `expansion_V5_T2-09_silen_beth_israel.json` | 2 | 02 | Silen/Beth Israel lineage |
| `expansion_V5_T2-10_kocher_nobel.json` | 2 | 12, 14 | Kocher Nobel lineage and governance |
| `expansion_V5_T3-01_ucsf_chain.json` | 2 | 02 | UCSF institutional succession |
| `expansion_V5_T3-02_stanford_chain.json` | 0 (1 upgrade) | 02 | Holman→Stanford citation upgrade to PMID |
| `expansion_V5_T3-03_vanderbilt_depth.json` | 2 | 02 | Vanderbilt institutional depth |
| `expansion_V5_T3-04_emory_depth.json` | 3 | 02 | Emory depth: Cushing→Elkin, Elkin→Emory, Emory succession |
| `expansion_V5_T3-05_michigan_succession.json` | 2 | 02 | Michigan institutional succession |
| `expansion_V5_T3-06_hopkins_modern_succession.json` | 2 | 02, 12 | Hopkins modern succession (Kirk, Allen) |
| `expansion_V5_T3-07_mattox_ben_taub.json` | 2 | 09 | Mattox/Ben Taub trauma lineage |
| `expansion_V5_T4-06_nyhus_hernia.json` | 2 | 08 | Nyhus hernia lineage |
| `expansion_V5_T4-08_organ_urm.json` | 2 | 14 | Organ/URM contributions |
| `expansion_V5_T4-09_hendren_mgh.json` | 2 | 08 | Hendren/MGH pediatric surgery |

### Citation Corrections

| PMID | Issue | Resolution |
|------|-------|------------|
| 18294269 | Resolved to wrong article (Perera, Colorectal Dis) | Upgraded to DOI: 10.1016/j.jpedsurg.2008.01.016 (Folkman memorial, J Pediatr Surg 2008) |
| 33421312 | Resolved to wrong article (Choi, Acta Ophthalmol) | Upgraded to DOI: 10.1007/bf02586849 (St. Mark's training program, Dis Colon Rectum 1980) |
| 37601473 | Journal mismatch in expected table | Confirmed correct: Bharani & Yeo, Ann Surg Open 2023 (not Plast Reconstr Surg) |

### New Nodes (37)

**Persons (33):** Walter G. Wolfe, R. Randal Bollinger, Robert W. Anderson, W. Randolph Chitwood Jr., James L. Cox, Thomas L. Spray, Robert H. Jones, J. Alex Haller Jr., C. Rollins Hanlon, James Jude, William Muller, H. William Scott Jr., E. Stanley Crawford, George P. Noon, Kenneth L. Mattox, George C. Morris Jr., H. Edward Garrett Sr., Oscar Creech Jr., Richard L. Varco, Henry Buchwald, Mark M. Ravitch, Jonathan E. Rhoads, Robert M. Zollinger, Keith Reemtsma, Judah Folkman, William Silen, Theodor Kocher, Lloyd M. Nyhus, Claude H. Organ Jr., W. Hardy Hendren III, James Barrett Brown, Norman Thompson, Allan Kirk

**Institutions (4):** Ben Taub General Hospital Department of Surgery, Vanderbilt University Department of Surgery, Boston Children's Hospital Department of Surgery, Beth Israel Hospital Department of Surgery

### Structural Impact

1. **Training tree depth.** V5's largest structural contribution is extending the major training trees. Sabiston's 8 trainees create the graph's widest training fan. The Blalock→Sabiston→Bollinger→Kirk chain is 4 generations deep. Combined with the DeBakey and Wangensteen trees, the graph now documents the complete mid-20th-century dispersal of Halstedian surgical training across the US.
2. **Component bridging.** Five component bridges (Jackson/Jefferson, ABOHNS/ABMS, Thompson/Michigan, ASBrS/ACS, St. Mark's/ASCRS) reduced connected components from 10 to 3. The two remaining 3-node islands (Bunnell/hand surgery and Clayman/endourology) lack documented PMID-backed connections to the main graph.
3. **Edge type rebalancing.** Direct_training edges (108) now exceed institutional_founder edges (83) for the first time, reflecting V5's focus on person-to-person training relationships rather than institutional founding.
4. **Institutional succession chains.** New succession chains at UCSF, Stanford, Vanderbilt, Emory, Michigan, and Hopkins create multi-generational institutional narratives previously limited to Duke and Hopkins.
5. **Pre-Halsted bridge.** The Hunter→Physick edge (1780) extends the graph's temporal range and connects the British surgical tradition to the earliest American surgical lineage.
6. **Folkman angiogenesis.** The Gross→Folkman→Boston Children's chain documents one of surgery's most significant contributions to cancer biology, extending the Ladd→Gross pediatric surgery lineage.

### Flags for Manual Review

1. **PMID 10359266** (expansion_V5_T1-03_plastic_surgery_bridge): Article is about Blair (MeSH person), not Brown directly. Brown (James Barrett) is mentioned in article body. Soft pass — consider finding a more specific Brown citation.
2. **PMID 25135240** (expansion_V5_T1-01_sabiston_training_tree): Article is about Sabiston (MeSH person). Anderson, Cox, and Spray are documented as trainees in article body but not in indexed fields. Soft pass.
3. **Remaining small-island components (2):** Bunnell/ASSH/Army Hand Centers (3 nodes) and Clayman/Endourological Society/WashU Urology (3 nodes). No PMID-backed bridge edges identified.
4. **V4 flags 1–9 above** remain open for review.

## 12. Citation Verification Pipeline (2026-03-17)

### Overview

A four-phase citation verification pipeline was applied to all PMID and DOI edges in the graph. The pipeline identified that many PMIDs in the original dataset resolved to completely unrelated articles (e.g., PMID 2446524, used for 4 Halsted training edges, resolved to "Isolation of RNA for dot hybridization by heparin-DNase I treatment of whole cell lysate" in Analytical Biochemistry 1987). These were systematic errors from the original build process, not random typos.

### Phase 1: Existence Verification

Verified that each PMID/DOI resolves to a real PubMed/CrossRef record via batched efetch and CrossRef HEAD requests. 137 unique PMIDs and 8 unique DOIs checked. 3 failures flagged (2 PMIDs returned no article, 1 DOI returned HTTP 404).

### Phase 1.5: Content-Match Validation

For each verified PMID/DOI, scored the article's title, abstract, and authors against the edge's source/target names and notes using token overlap. Classification: score >= 0.20 = content_match, 0.05-0.19 = weak_match, < 0.05 = MISMATCH. Results: 97 content_match, 51 weak_match, 60 MISMATCH.

### Phase 1.75: Candidate Search

For all 111 flagged edges (60 mismatch + 51 weak), searched PubMed via tiered esearch queries (relationship-specific, name-only, obituary/tribute, journal-specific) and CrossRef as fallback. Found candidates for 85 edges (158 PMID + 12 DOI candidates). Produced `CITATION_REPAIR_CANDIDATES.md` for manual adjudication, reviewed via `citation_adjudicator.html`.

### Phase 2: Adjudicated Repair

Applied all 111 manually reviewed decisions:

| Action | Count | Description |
|--------|------:|-------------|
| ACCEPT | 52 | Replaced bad PMID/DOI with verified candidate (50 PMID + 2 DOI) |
| ARCHIVE | 32 | Downgraded to institutional_archive — no PubMed source exists |
| DELETE | 4 | Removed unverifiable edges |
| KEEP | 23 | Retained current citation after manual review |

**Deleted edges:** Sabiston→Wolfe (direct_training), Sabiston→Anderson (direct_training), Sabiston→Spray (direct_training), Najarian→ASA (governance_leadership). Full content preserved in `archive/phase2_deleted_edges.json`.

**Re-verification:** All 52 newly inserted PMIDs/DOIs passed both existence and content-match verification (52/52, 100%).

### Reports

| File | Description |
|------|-------------|
| `verification_report_phase1.json` | Phase 1 existence check results and PMID metadata |
| `verification_report_phase1_5.json` | Phase 1.5 content-match scores, weak matches, and mismatches |
| `CITATION_REPAIR_CANDIDATES.md` | Phase 1.75 candidate search results (human-readable) |
| `citation_repair_candidates.json` | Phase 1.75 candidates with adjudicated action values |
| `citation_adjudicator.html` | Interactive adjudication tool |
| `verification_report_phase2.json` | Phase 2 application results and re-verification |
| `archive/phase2_deleted_edges.json` | Full content of 4 deleted edges |

## 13. Phase 2.5 Citation Upgrade Campaign (2026-03-18)

### Overview

A targeted PubMed search campaign identified verified PMID citations for 35 edges previously backed only by institutional_archive evidence. Seven changeset files (batch1–batch7) were generated and applied across 12 module files. Nine edges initially flagged verification_required were resolved through secondary-source verification. One structural graph error was corrected.

### Citation Upgrades (34 applied, 1 reverted)

| Batch | Module(s) | Upgrades | Key PMIDs |
|------:|-----------|:--------:|-----------|
| 1 | 05_urology, 11_mis_robotic, 14_global_military | 7 | 20620396, 17437775, 11923603, 3545417, 20134311, 5762414 |
| 2 | 01_halsted_core, 03_neurosurgery, 06_orthopedics | 8 | 12984268, 33307257, 8692401, 10941999, 7965131, 18196367 |
| 3 | 07_oncology_trials, 09_trauma_acute_infection | 3 | 34991349, 8686806, 12984268 |
| 4 | 04_cardiothoracic_vascular, 10_quality_outcomes | 6 | 26635916 |
| 5 | 08_subspecialties | 4 | 3095882, 25858011, 3095885 |
| 6 | 12_governance_societies | 2 | 4559844 |
| 7 | 02_general_surgery_spread | 3 | 4559844, 12984268 |

### Verification Flag Resolution (9 resolved)

Eight edges were confirmed through secondary-source verification and had verification notes appended. One edge was reverted:

**Reverted:** Hopkins→Blakemore (01_halsted_core.json). Blakemore's training dates (1922–1926) begin the year Halsted died (September 1922). Carter 1952 (PMID 12984268) enumerated only Halsted's own appointees (17 residents + 55 assistant residents through 1922). No secondary source confirms Blakemore appears in Carter's enumeration. Evidence reverted to institutional_archive.

**Confirmed (8):** Halsted→Homans, Halsted→Naffziger, Hopkins→Firor, Hopkins→Hart, Reid→Altemeier, Gross→Hendren, Gross→Koop, Graham→Moyer.

### Structural Correction: Ponsky/SAGES

PMID 29362909 identifies Gerald Marks — not Jeffrey Ponsky — as the founder of SAGES (1981). The existing Ponsky→SAGES society_founder edge was reclassified to governance_leadership (SAGES president 1990–91) and moved from 11_mis_robotic.json to 12_governance_societies.json. A new Gerald Marks→SAGES society_founder edge was created in 11_mis_robotic.json. This is a net +1 edge (382 total) and +1 node (Gerald Marks, 318 total).

### Impact on Evidence Distribution

PMID-backed edges increased from 168 (44.1%) to 204 (53.4%). For the first time, PMID citations outnumber institutional_archive citations (204 vs 169). This represents a milestone in the graph's evidence quality: the majority of edges are now backed by PubMed-indexed publications.
