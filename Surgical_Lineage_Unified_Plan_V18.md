# Surgical Lineage Atlas — Unified Plan
## v18

**Author:** Ankit Sarin, MD
**Date:** 2026-07-25
**Status:** V17 cycle landed — four commits: schema hardening + `preceptor-untitled` token (`0f3e43e` predecessor `1ed22d1`), invariant/snapshot split (`0f3e43e`), connectivity demotion (`8bacde0`), V17-B1 merge (`97035fe`), `society_verified` removal (`27de824`). Graph at **559 edges / 429 nodes / 4 components** (fragmentation intentional). `origin/main` at `27de824`; canonical sha256 `5614bb324e473ad5f7daa9c675db052efef15c01f73279f66512e2261006ed20`. The institution-sourced `direct_training` class is resolved to two deliberately-held edges (Hart, Safar). Next cycle tags `v17_b2` (pre-Halsted apprenticeship batch).

---

## 1. What This Is

A citation-backed directed knowledge graph mapping the training lineages, institutional founding chains, and professional society networks of American surgery from 1777 through the present. The project sits at the intersection of digital humanities, surgical history, and network science, with goals spanning academic publication, open dataset contribution, and surgical education. Operates under the Digital Surgeon research initiative brand.

## 2. Architecture

**Graph schema (v3.2):** JSON edge arrays conforming to `00_schema.json` (draft-07). **Nine edge types:** `direct_training`, `observational_study`, `institutional_founder`, `institutional_succession`, `society_founder`, `governance_leadership`, `programmatic_accreditation`, `institutional_parent`, `residency_at`. Three node types: `person`, `institution`, `society`. **Three evidence types: `PMID`, `DOI`, `institutional_archive`.** `end_year` is an `["integer","null"]` union — null denotes an ongoing relationship, paired with `temporal_range: "<start>-ongoing"`; the key remains required. No sentinel year: temporal analysis is planned and a sentinel would silently corrupt date arithmetic. jsonschema is wired into `phase_h` in **warn-only** mode (reports violations, never changes exit code); flipping it to blocking is a separate future decision.

**`residency_at` semantics:** person → institution (trainee → program), a *fallback* for documented structured-program completion where no qualifying individual PD/APD is identifiable, or the era predates formal PD structure. Any era. `direct_training` is strictly preferred whenever a qualifying PD/APD exists; a `direct_training`-first search is a precondition for every candidate. **Machine-checkable gating (`diagnostic_audit.py` Audit 4, blocking):** notes must carry exactly one token from `{mentorless-by-committee, pre-PD-era, director-unidentified, preceptor-untitled}`. `preceptor-untitled` (added V17) means the preceptor is **identified by name but holds no documented structural title** — distinct from `director-unidentified`, where the person is unknown. **Projection:** double-excluded from the person↔person lineage view; included in full-graph metrics.

**Storage:** 15 module files (`01`–`14` thematic + `15_institutional_hierarchy.json`), `00_schema.json`, the regenerated canonical flat file, and auxiliary `node_labels_adjudicated.json` (`label_short`; not regenerated into canonical).

**Visualization:** `explorer_template.html` is the durable design-of-record; `build_explorer.py --version` regenerates from canonical + labels. Current build `surgical_lineage_atlas_v16_b2.html` is **stale** (428/561) and needs a rebuild at v17_b1.

**Merge & validation pipeline (config-driven, stable since V12):** `phase_i_merge.py` (route by `route:` tag, pre-insert duplicate-triple check, manifest A `edge_modify_fields` + B `edge_semantic_ops` with `delete`/`reverse_retarget`/`reclassify` handlers, all guarded by `expected_existing` + unique-match), `phase_g_labels.py`, `phase_h_apply.py` (canonical regen + derived-delta gate + invariants + warn-only schema validation), `diagnostic_audit.py` — all driven by `pipeline_config.json`. Per-run variables are CLI args, not code edits. **Handler contracts:** `find_unique` matches on `source_node + target_node + edge_type` only; additional guards go in `expected_existing`. `reclassify` and `reverse_retarget` both apply an unrestricted `set` verbatim, so an endpoint flip and a type change ride in one guarded op. `preserve[]` asserts named fields did **not** change. `phase_i` has no additive-only mode — additive batches pass **empty no-op manifests**.

**Invariants (post-V17):** `zero_duplicate_triples`, `zero_node_type_conflicts`, `label_node_parity`, and the Audit 4 token gate remain **hard and blocking**. **`single_component` was DEMOTED to a reported metric** (`component_report` in `pipeline_config.json`: `expected_components`, `max_island_size`) — it prints component count, sizes, and full member lists of every non-giant component, warns on threshold breach, and never blocks. Rationale, which must survive: the invariant was being satisfied *only* by three miscoded bridge edges, so enforcing it created standing pressure to author false data. Connectivity is a measured property of the current graph, not a property that must hold at every version.

**Analysis pipeline:** `networkx_diagnostic.py` — read-only, config-driven (`--version`, `--threshold`, `--top-n`). **Lineage subgraph is person↔person:** `edge_type ∈ {direct_training, observational_study}` **and** both endpoints `node_type == person`. **Reachability ≠ lineage** — load-bearing for the manuscript. **Invariant/snapshot split completed (V17):** true invariants stay hard asserts (`G_train` all-persons, trunk-roots all-persons, canonical sha, single-component *of the training graph*, betweenness finiteness, root-pair reachability); version snapshots (node/edge totals, trunk-root sets, floater counts, full-graph component count) are now printed INFO. Baselines no longer re-stale at every expansion; `TASK V15-DIAG-BASELINE` is **closed**.

**Division of labor:** claude.ai (planning chat) handles architecture, research, citation verification, JSON/expansion authoring, Claude Code prompt drafting, manuscript strategy, the unified plan, and analysis design. Claude Code (MacBook) handles file operations, merges, canonical regeneration, the explorer rebuild, audits, analysis-script runs, and git.

**Key methodological decisions (stable):**
- Training edges restricted to documented PD/APD roles; informal mentors without structural titles excluded. **Mentorship without a structural title does not qualify** (Holman→Hughes is the canonical hold; Derby→Blakemore and Warren→Fazio are the V17 instances, both resolved to `preceptor-untitled`).
- **`direct_training` must be person→person.** An institution-endpoint `direct_training` edge is a data-model defect. *(The V17 Plan claimed zero remained after V16-B2; that was false — eight existed. Seven were `direct_training`, one `observational_study`. Six resolved in V17-B1; two remain deliberately held.)*
- **`observational_study` MAY take an institution source** when the documented fact is a study visit to an institution (e.g. St. Mark's→Mathews 1877–78). Travelling to observe an institution's practice was a real educational mode; this is not the `direct_training` defect. Restricted to pre-1950 (Mouret→Dubois→Reddick grandfathered).
- **Degree attainment is out of scope, not recoded.** Matriculation-to-MD spans are not training relationships and get no edge type. Three such edges (Firor, Flint, Jackson) were deleted rather than relabelled; `medical_education_at` was considered and **rejected** as a speculative type addition. Revisit only if a future batch produces a dozen or more genuinely load-bearing degree facts.
- `governance_leadership` directionality: person → (institution | society). Dean/VC/CEO and general academic-administration roles out of scope.
- Evidence tier: **PMID > DOI > institutional_archive.** PMID/DOI citations are citation-mcp-verified (**content-match, not existence**) before entering an artifact; `institutional_archive` accepted for founding/biographical/appointment facts. **A `society_verified` tier was added and then removed** — speculative, zero usage; re-add only alongside the first real society-sourced edge, when the data shape is known rather than assumed.
- Canonical naming: one root per real-world institution; sub-unit `<Root Name> <Descriptor>`, root must exactly prefix every child ID.
- `institutional_parent` start_year = sub-unit founding year.
- **Delete-batch discipline:** every proposed delete is connectivity-dry-run before authoring. **Full manifest dry-run is now standard:** simulate every `expected_existing` guard, every `preserve` field, and all post-merge counts against canonical in the planning chat before handoff. V17-B1 matched its simulation exactly on all nine gates.

## 3. Current State

| Metric | v17_b1 (committed `97035fe`, schema `27de824`) |
|--------|-----------------------------------------------:|
| Total edges | 559 |
| Total nodes | 429 |
| Connected components | **4** (intentional) |
| Node types | person 224 / institution 149 / society 56 |
| Schema version | v3.2 (9 edge types, 3 evidence types) |
| Current explorer | `surgical_lineage_atlas_v16_b2.html` — **STALE**, needs rebuild |
| Structural audit | 0 blocking; 0 person-name flags; Audit 4: **5** `residency_at` edges, 0 violations |
| Test suite | 34 collected / 34 passed |

**Edge-type distribution:** governance_leadership 166, direct_training 129, institutional_founder 98, society_founder 61, institutional_parent 49, programmatic_accreditation 24, institutional_succession 18, observational_study 9, residency_at 5.

**Module inventory (edges):** 01:15, 02:135, 03:32, 04:44, 05:12, 06:12, 07:20, 08:73, 09:21, 10:21, 11:15, 12:90, 13:5, 14:15, 15:49.

**Components (4):** giant 422; **Yale island (3)** — Gustaf Lindskog, Joseph Marshall Flint, Yale University Department of Surgery; **ABEA island (2)** — American Broncho-Esophagological Association, Chevalier Jackson; **SUS island (2)** — Society of University Surgeons, Warfield Firor. These appeared when the three miscoded degree edges were deleted; they are the honest current state, not a regression.

**Lineage projection (`G_train`) — unchanged by V17-B1:** 154 nodes / 135 edges / 24 weak components / 4 major (≥5). All V17-B1 edits touched institution-endpoint edges, which were never in the projection, and Dean Lewis has no training edge. The 80-node super-trunk carries five roots (Ochsner, Langenbeck, Zuidema, Taussig, Ladd); satellites W.J. Mayo (12), E.P. Richardson (5), Blair (5). **Major trunk roots: 8, unchanged.** Root-pair reachability holds (18 cross-trunk pairs, 0 unreachable) — verified to survive fragmentation because no island member is in `G_train`.

**Betweenness (v16_b2, interim — NOT re-run post-merge):** full-graph undirected is institution/society-dominated (ACS 0.452, ASA 0.206, Halsted 0.166, Blalock 0.158); in the undirected *projection* **Blalock (0.196) exceeds Halsted (0.170)** as top person bridge — candidate headline result. `G_train` is unchanged by V17-B1 so projection figures should hold, but the full-graph values shifted with 559 edges / 4 components and need a fresh committed run.

**Repo:** clean on `origin/main` at `27de824`. Session chain: `1ed22d1` (schema hardening + `preceptor-untitled`) → `0f3e43e` (invariant/snapshot split) → `8bacde0` (connectivity demotion) → `97035fe` (V17-B1 merge) → `27de824` (`society_verified` removal). Backup at `backups/v17_b1_20260725T200010Z/`. **This plan is now tracked in git** (was untracked through v17).

**Collaborator group:**

| Person | Institution | Role | Active Task |
|--------|------------|------|-------------|
| Ankit Sarin | UC Davis | PI, graph architect | pre-Halsted batch, manuscript |
| Adnan Alseidi | UCSF | ACS board liaison, HPB connections | ACS dissemination positioning |
| Talar Tatarian | Jefferson | FC data lead | FC letter — **unsequenced, nothing waits on it** |
| Nova Szoka | WVU | MIS/fellowship hypothesis | MIS lineage conceptual framework |

## 4. What Changed This Session

- **Institution-sourced training class audited and resolved.** The V17 Plan's claim that zero institution→person `direct_training` edges remained was false; eight existed. Root-cause analysis found **three distinct problems wearing one label**: named-but-untitled preceptors (Blakemore, Fazio), degree attainment miscoded as training (Firor, Flint, Jackson), and a genuine citation failure (Safar). Merged as V17-B1: 3 deletes, 2 `reverse_retarget` conversions, 1 new node. 561→559 edges, 428→429 nodes, 1→4 components. All nine acceptance gates matched the dry-run simulation exactly.
- **Four schema/tooling commits.** `end_year` null union + jsonschema warn-only wiring; `preceptor-untitled` reason token; invariant/snapshot split across `test_v16_pr.py` and `networkx_diagnostic.py` (closing `V15-DIAG-BASELINE`); `single_component` demoted to a reported metric; `society_verified` added then removed.
- **Dean DeWitt Lewis node added** — `governance_leadership` → JHH Dept of Surgery, 1925–1939, Chesney Archives record confirmed at merge time. Closes the post-Halsted leadership gap (Halsted d. 1922 → Blalock 1941). He carries no training edge and is **not** in `G_train`.
- **Three contrarian catches pre-authoring.** (a) Reading the actual edge objects invalidated two proposed Halsted re-attributions — Firor's and Flint's spans are degree dates, and Flint's own notes disclaim Halsted training. (b) `medical_education_at` was proposed by the architect, then withdrawn on consistency grounds after connectivity testing showed the "bridge" motive was the defect, not the justification. (c) `society_verified` was accepted into the schema despite the same speculative-addition argument that had just been used to reject `medical_education_at` — inconsistency caught by the PI, tier removed.
- **FC assessment corrected.** FC accredits a **one-year post-residency subspecialty fellowship** (advanced GI/MIS, bariatric, HPB, foregut) — not general surgery residency, and not the PD relationship the atlas is built on. It was previously overweighted in this plan as "the repair for the censored modern tail." It is not; see §5.4.
- **Two `[VERIFY_NAMES]` debts surfaced** on the Carter 1952 citation (PMID 12984268) for Firor and Hart — applied in Phase 2 without confirming either man appears in Carter's enumeration. The Firor edge is now deleted; the Hart debt remains open.

## 5. Open Issues & Blockers

1. **Hart and Safar (held).** The two surviving institution-endpoint `direct_training` edges. **Hart** is genuinely contested: PMC7828946 (Wright & Schachar 2020) calls him "a former Halsted resident," but his program dates (intern 1921–22, assistant resident 1923–27, resident surgeon 1927–29) put most of his training after Halsted's death, under the interregnum and Dean Lewis. "Halsted resident" is a term of art meaning *trained in the Halsted system*. Also carries an unresolved `[VERIFY_NAMES]` flag. **Safar**: PMID 35839834 is a journal-centennial review that does not establish his 1954 Hopkins surgical training — content-match failure; needs a replacement citation, and carries a separate anesthesiology-scope question.
2. **Definitional denominators unpinned — manuscript risk.** Three headline numbers depend on unstated denominators: trunk roots (**30** raw in-degree-zero in `G_train` vs **8** major-component-gated), root pairs (**28** pairwise vs **18** cross-trunk), components (**4** full-graph vs **24** weak in `G_train`). Each is defensible alone; together they invite a reviewer challenge. Pin all three in one place and report with denominators visible **before** any structural claim is drafted.
3. **No current committed diagnostic run.** V17-B1 diagnostics were generated for the gates then removed to keep the commit confined. A quotable `networkx_diagnostic_v17_b1` run needs regenerating and committing, along with the explorer rebuild (current build is 428/561).
4. **The modern tail is structurally censored and cannot be repaired.** Post-1990 `direct_training` collapses to ~1 edge/decade — ascertainment lag, not a change in training. ACGME does not publish trainee-to-PD pairings; documented lineage comes from historiography (obituaries, festschrifts, institutional histories) which accumulates with a decades-long lag. **This is a property of the evidence, not a gap in collection.** No workstream fixes it. Consequences in §7.
5. **Reference docs stale.** `README.md` + `SURGICAL_LINEAGE_ATLAS.md` still at V13 counts / "8 edge types". Canonical `module` field covers ~320/559 edges. Data-dictionary §7/§8 describe the retired pipeline in present tense. All non-blocking.
6. **citation-mcp cache-collision defect.** Bulk verification can return one cached record for multiple distinct identifiers. Mitigation: `force_refresh` + homogeneity check. Fix candidate: cache-key audit on the citation-mcp server (Digital Surgeon infra; separate from graph work).
7. **Name-collision pre-emption.** "John Hunter" is correctly the 18th-century anatomist (2 edges, →Physick 1788, →Cline 1777). The collision becomes live the moment a modern John G. Hunter enters. The pre-Halsted batch raises that likelihood — decide the disambiguation naming convention **before** `v17_b2`, not after. Relatedly, `networkx_diagnostic` test 4 asserts John Hunter in-degree 0, which the pre-Halsted batch may legitimately break; convert it to a snapshot when it does.

## 6. Next Steps

1. **Pre-Halsted apprenticeship batch (`v17_b2`) — scope first.** Three chains: Philadelphia (Hunter→Physick already anchored, extend through Randolph/Gross and the Penn/Jefferson chairs), New York (Post→Mott→Parker, P&S/Bellevue), Boston/MGH (the Warren father-son line, Bigelow). Target 18–28 edges: roughly 8–12 person-to-person preceptorship, 10–16 structural. **Pre-commit before authoring:** (a) institutional naming decisions for Penn/Jefferson/P&S/Bellevue/MGH, whose 18th–19th-century identities are tangled and will otherwise generate root-prefix violations at merge; (b) the John Hunter disambiguation convention; (c) the `observational_study` sensitivity analysis in §7, since this batch will multiply that edge type several-fold.
2. **Definitional pinning (§5.2)** — short analysis-design task, blocks manuscript drafting not the next batch.
3. **Regenerate and commit diagnostics + explorer** at v17_b1 (§5.3).
4. **Hart/Safar resolution** — two edges, real evidentiary questions, no downstream dependency. Hart needs the Halsted-vs-Lewis attribution settled; Safar needs a replacement citation.
5. **Era-composition figure** (§7) — design after the pre-Halsted batch lands, since that batch is the only remaining workstream that materially improves it.
6. **Docs refresh** — `README.md` + `SURGICAL_LINEAGE_ATLAS.md` (docs-only, rides any session).
7. **Manuscript freeze criterion** — decide what graph state locks the figures, so diagnostics stop being "interim" at a defined point.

## 7. Publishing & Dissemination Path

**Manuscript:** Knowledge-graph structural analysis (not a history paper). Core contributions: betweenness centrality identifying non-obvious bridge figures; shortest-path structure between independent trunk roots; the census of subspecialty society-to-board spawning events; the institutional-hierarchy layer. **The reachability-vs-lineage distinction is an explicit methods point.** Worked examples: Hughes→Rich (full-graph-reachable, projection leaf) and the Mount Sinai cluster (governance-complete, lineage island but for Starzl→Shapiro). **Blalock exceeding Halsted in undirected person-bridge betweenness** is the candidate headline. The three islands are now a *reported finding* rather than an artifact to be papered over.

**Era-composition figure (defensible weak form).** The strong claim — dating the apprenticeship → society → institutional transition from the graph — is **indefensible**: the schema encodes the era boundaries it would purport to discover (circularity), edge density measures historiographic attention rather than training prevalence (ascertainment), and 9 `observational_study` edges cannot anchor a changepoint against 129 `direct_training`. The defensible form is descriptive decade composition with exogenous anchors overlaid (Hopkins residency 1889, AMA CME 1904, Flexner 1910, ACS 1913, ABS 1937, RRC 1950s, ACGME 1981, FC 1997), framed as a **validity check on the graph**. Given §5.4, present **two series side by side** — training-relationship density (explicitly truncated ~1990, censoring stated) and institutional-structure density (`programmatic_accreditation`, `governance_leadership`, `society_founder`, which are not lag-bound and do carry the modern era). Never a single composite curve: it would invite reading the training decline as a finding. **Mandatory sensitivity analysis:** recompute excluding the schema-constrained types (`observational_study`, `residency_at`) and show the pattern survives in the unconstrained ones. If it does not survive, publish the network metrics without the era claim.

**Society partnerships — conservative assessment.** FC is a single society accrediting one-year subspecialty fellowships; it is not a comprehensive source and would not repair the modern tail. Its realistic value is a methodological proof-of-concept plus, if it lands, a *complete bounded subgraph* of one subspecialty's fellowship training over ~25 years — which would permit direct estimation of ascertainment bias against the curated historical graph. That is a genuine contribution but a hypothetical one from an unscheduled partnership. **Nothing is sequenced behind it.**

**Target journals (ranked):** 1) *Journal of Surgical Education* (Elsevier, Q1) — primary, UC OA covered; 2) *Surgery* (Elsevier) — higher-impact backup, UC OA covered; 3) *Medical Teacher* (Taylor & Francis) — cost-advantaged, UC OA covered.

**Dissemination:** ACS Clinical Congress (Adnan to time), SAGES (MIS fit), interactive explorer as supplementary or standalone resource.

## 8. Workflow Convention

**Planning (claude.ai):** architecture, research, citation verification, expansion specs, Claude Code prompts, manuscript strategy, analysis design, unified plan. **Execution (Claude Code, MacBook):** file ops, merges, canonical regeneration, explorer rebuild, audits, analysis-script runs, git.

**The core loop:** this chat produces a route-tagged expansion file (bare array; `route: <full_route_map_key>` in each edge's notes) plus manifests with `expected_existing` guards. **Every batch is fully dry-run simulated here before handoff** — guards, `preserve` fields, post-merge counts, component structure — and the handoff states predicted values as acceptance gates so any deviation stops the merge. PMID/DOI citations are citation-mcp-verified (**content-match**) before authoring; on suspiciously homogeneous bulk results, re-verify with `force_refresh`. **Never fabricate a locator** — if a URL cannot be confirmed, make confirmation a blocking pre-merge step for Claude Code rather than constructing one by pattern (V17-B1 Step 0 is the template). Low-blast-radius file/Python tasks run `--dangerously-skip-permissions`; git/systemd/system config never do. Git: straight to `main`, push, no branches. **Script/tooling changes commit separately from graph merges.**

**Iterative process:** Outline → web/PubMed search (offered) → confirm → expand → refine. One batch at a time, explicit approval gates, mandatory contrarian/scope review before authoring. The architect owns spec errors: hold the commit, issue a corrective spec, re-run, then commit. **Two recurring architect failure modes to watch, both observed in V17:** reasoning forward from what a node *should* imply instead of checking what it actually connects to (produced two wrong re-attributions and one wrong claim about Lewis); and applying inconsistent standards to structurally identical decisions (`medical_education_at` rejected, `society_verified` accepted). Read the actual edge objects and simulate before proposing dispositions.

## 9. Execution Pipeline (config-driven, on MacBook)

| Component | Role |
|-----------|------|
| `pipeline_config.json` | Static: 15-module route map, repo paths, hard invariants, `component_report` thresholds, `name_pair_whitelist`. |
| `phase_i_merge.py` | Merge — route by tag, duplicate-triple check, manifest A/B guarded handlers (requires both args; empty for additive). Emits `merge_run_<version>.json`. |
| `phase_g_labels.py` | Label reconcile — append stubs, prune removed, `--max-prune` guard, per-id byte-stability check. |
| `phase_h_apply.py` | Canonical regen + derived-delta gate + hard invariants + component report (non-blocking) + warn-only schema validation. |
| `diagnostic_audit.py` | Read-only name/temporal/dedup audits + Audit 4 (4-token gate, blocking) + island member listing. |
| `build_explorer.py` | `--version`-aware explorer builder. |
| `networkx_diagnostic.py` | Read-only structural analysis. Lineage subgraph = person↔person. Hard asserts are true invariants only; version snapshots print as INFO. |

**Merge invocation:** `phase_i_merge.py --expansion <batch>.json --manifest-a <A|empty>.json --manifest-b <B|empty>.json --version v<N> --config pipeline_config.json` → `phase_g_labels.py` → `phase_h_apply.py --version v<N> --run-record merge_run_v<N>.json` → `diagnostic_audit.py --version v<N>` → `build_explorer.py --version v<N>`.

**Analysis (read-only):** `networkx_diagnostic.py --version v<N> --config pipeline_config.json [--threshold 5 --top-n 25]`.

**Environment:** system `python3` is PEP-668 externally-managed; the pipeline runs from the project `.venv`.

Archived (`archive/`, flat): spent pipeline scripts and batch inputs through all V16 inputs. V17-B1 inputs (`v17_b1_expansion.json`, both manifests) await archival. `backups/` holds per-merge rollback snapshots.
