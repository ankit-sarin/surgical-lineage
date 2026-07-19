# Schema PR — add `residency_at` edge type (v3 → v3.1) — REVISED

**Status:** REVISED 2026-07-18 after contrarian review (supersedes the pre-V15 draft). V16-B1
(MASH→Rich retarget, commit 0f0d5e4) is landed; this PR is next. Sequence: land schema (small
Claude Code task with mandatory pre-flight) → Batch 3 research + authoring in chat → merge as
V16-B2 (explorer rebuild and batch-input archiving ride along).

## Rationale
A residue of training relationships tie a person to an institution's *program* but have no
qualifying individual PD/APD: mentorless-by-committee (Coller — first MGH surgical resident, 1912,
appointed by unanimous attending vote, no single chief), pre-PD-era fellowship (R. Lee Clark —
Mayo fellowship 1935–39, no named era-preceptor), director-unidentified-after-search (Leffall —
MSK surgical-oncology senior fellowship 1957–59), and newly, Rich — Letterman General Hospital
general surgery residency c. 1961–65, pending a PD search (see table). Keeping these as
`institution→person direct_training` is exactly what contaminated the V13 lineage projection (the
27-edge REVIEW set); deleting them discards real structural fact; and they cannot become
person↔person because no qualifying person exists. `residency_at` records the institutional
training relationship honestly without asserting a false person-to-person mentorship.

## The type
- **Name:** `residency_at`
- **Direction:** person → institution (trainee → program), parallel to the `governance_leadership`
  person→institution convention (validated again by the V16-B1 retarget).
- **Semantics:** documented completion of a structured residency/fellowship at an institution's
  program where no qualifying individual PD/APD is identifiable, or the era predates formal PD
  structure. Any era (unlike `observational_study`, which stays pre-1950).
- **Gating (anti-scope-creep), machine-checkable:** requires (1) documented structured-program
  completion — not mere affiliation/employment; (2) a fixed reason token in `notes`, exactly one of:
  `[residency_at_reason: mentorless-by-committee]`
  `[residency_at_reason: pre-PD-era]`
  `[residency_at_reason: director-unidentified]`
  — free-prose justification accompanies the token but does not replace it; (3) standard citation
  discipline (PMID/DOI/institutional_archive, content-match). `direct_training` remains strictly
  preferred whenever a qualifying PD/APD exists — `residency_at` is a fallback, never a
  convenience. A `direct_training`-first search is a precondition for every candidate and its
  outcome is recorded in the edge notes.

## Projection behavior
- **Lineage projection (person↔person):** EXCLUDED automatically — institution endpoint *and*
  edge_type outside `{direct_training, observational_study}`. Double-excluded and self-documenting;
  the exclusion becomes structural rather than a filter on a mislabeled edge.
- **Full-graph betweenness / geodesics:** INCLUDED (institutions already appear legitimately as
  intermediaries).

## Mandatory Claude Code pre-flight (before any file change)
The "no pipeline_config change" claim below is *conditional* and must be converted to certainty:
1. Grep `pipeline_config.json`, `phase_h_apply.py`, `phase_i_merge.py`, `phase_g_labels.py`,
   `diagnostic_audit.py`, and `networkx_diagnostic.py` for hardcoded edge-type literals or
   enumerations (any list containing e.g. `"programmatic_accreditation"`). If any structural
   invariant or validation step carries its own edge-type list, it must accept `residency_at`, and
   that file joins the change list.
2. Confirm phase_h's by-edge-type delta gate handles a type key absent from `pre` (new type with
   pre=0). If it iterates only over `pre` keys, the gate either crashes on or silently ignores a
   new type — patch to a full-key union before Batch 3.
3. Report both findings before making changes; if either requires more than a localized fix, stop
   and hand back.

## Files to change (Claude Code, MacBook)
1. **`00_schema.json`** — add `"residency_at"` to `items.properties.edge_type.enum` (8 → 9 types);
   bump the `title` string "… - V3 Institutional Hierarchy" → "… - V3.1" (the schema file carries
   no version field; the title string and the Unified Plan are where v3.1 lives).
2. **`pipeline_config.json`** — expected: no route-map change (routing is by module `route:` tag,
   not edge_type). Conditional on pre-flight item 1.
3. **`diagnostic_audit.py`** — two additions: (a) per-edge assert: every `residency_at` edge's
   notes contain exactly one `[residency_at_reason: …]` token from the fixed set (blocking
   finding otherwise); (b) harden the person-name similarity heuristic to flag middle-name-vs-
   initial patterns (same first and last name token, differing middle representation) — the
   Joseph M. Mathews / Joseph McDowell Mathews duplicate passed the V15-B2 and V16-B1 audits with
   0 person flags. A full-node sweep found this to be the only true person duplicate, so the
   hardened check should reproduce exactly one hit pre-consolidation and zero after.
4. **`networkx_diagnostic.py`** — one-line docstring/comment update on the lineage-projection
   predicate naming `residency_at` as an explicitly-excluded training-type-with-institution-
   endpoint. No logic change.
5. **README.md / SURGICAL_LINEAGE_ATLAS.md** — bump "8 edge types" → "9 edge types" during the
   next docs pass (already backlogged; not part of this PR's commit).

## Mathews node consolidation (must precede or ride within Batch 3)
"Joseph McDowell Mathews" and "Joseph M. Mathews" are the same person as two nodes.
Consolidate to the canonical full name **"Joseph McDowell Mathews"**:
- Retarget all "Joseph M. Mathews" edges (St. Mark's inbound; APS society_founder; APS
  governance_leadership) to the survivor node.
- The two `society_founder → American Proctologic Society (1899)` edges become semantic
  duplicates: keep the PMID 23997672 edge, delete the `institutional_archive` one.
- Net structural delta from consolidation alone: −1 node, −1 edge.
- Acceptance: hardened name heuristic reports 0 person flags post-merge.

## Batch 3 conversions (author after schema lands; research tasks in chat first)
Convert via `reclassify` + `reverse_retarget` (explicit new endpoints **including swapped
source/target node-type fields**, guards matched to state at op application time — both per the
V16-B1 run findings):

| # | Current edge | → New edge | Reason token / decision | Citation status |
|---|---|---|---|---|
| 1 | MGH Dept → Frederick Coller (direct_training, 1912–17) | Coller → MGH Dept, `residency_at` | mentorless-by-committee | PMID 14036574 (content-match to confirm); normalize temporal_range `"1912-c. 1917"` → `"1912-1917"` in same op |
| 2 | Mayo Dept → R. Lee Clark (direct_training, 1935–39) | Clark → Mayo Dept, `residency_at` | pre-PD-era | institutional_archive (Mayo_Archive_Clark) |
| 3 | MSK → LaSalle D. Leffall Jr. (direct_training, 1957–59) | Leffall → MSK, `residency_at` | director-unidentified (search to be re-run and documented) | **needs replacement citation** — 18481473 documents his chair, not this fellowship; research task in chat |
| 4 | St. Mark's → Joseph M. Mathews (observational_study, 1877–78) | **Allingham-first:** if PMID 23997672 content-matches William Allingham as preceptor → `observational_study | Allingham → Mathews` (pre-1950, person↔person, enters the lineage projection; requires new Allingham node). Fallback: Mathews → St. Mark's, `residency_at` | director-unidentified (fallback only) | PMID 23997672 (content-match decides the branch) |
| 5 | *(new edge)* | Norman Rich → Letterman General Hospital, `residency_at` (c. 1961–1965; requires new Letterman node) | director-unidentified — **only after** a genuine Letterman chief-of-surgery/PD search for those years (AMEDD archives); if a named chief is documentable, `direct_training` is used instead per the fallback rule | institutional_archive (USU/obituary record) pending the search outcome |

Rows 4 and 5 add nodes (Allingham and/or St. Mark's fallback; Letterman), making V16-B2 a mixed
modification+expansion batch — consistent with reserving the V16 version increment for it.

## Out of scope for this PR
Does not touch the V15/V16-B1 re-attributions or the Batch-2 Bucket-C deletes. Does not convert
the needs-node/needs-research holds (Hart, Blakemore, Flint, Jackson, Safar, Firor) — those await
interim-leadership nodes or scope rulings, not this schema. Does not build the Walter Reed /
USUHS / Hughes military-institutional cluster (V16+ candidate list in the Unified Plan). Explorer
rebuild and README/ATLAS count refresh ride with V16-B2, not this commit.
