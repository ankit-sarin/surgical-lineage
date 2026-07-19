# Schema PR — add `residency_at` edge type (v3 → v3.1)

**Status:** DRAFTED for Batch 3. Do **not** apply during the V15 Batch-1 merge. Land after Batches 1–2 commit, then run Batch 3 conversions.

## Rationale
A residue of training relationships tie a person to an institution's *program* but have no qualifying individual PD/APD:
mentorless-by-committee (Coller — first MGH surgical resident, 1912, appointed by unanimous attending vote, no single chief),
pre-PD-era fellowship (R. Lee Clark — Mayo fellowship 1935–39, no named era-preceptor),
director-unidentified-after-search (Leffall — MSK surgical-oncology senior fellowship 1957–59).
Keeping these as `institution→person direct_training` is exactly what contaminated the V13 lineage projection (the 27-edge REVIEW set); deleting them discards real structural fact; and they cannot become person↔person because no qualifying person exists. `residency_at` records the institutional training relationship honestly without asserting a false person-to-person mentorship.

## The type
- **Name:** `residency_at`
- **Direction:** person → institution (trainee → program), parallel to the `governance_leadership` person→institution convention.
- **Semantics:** documented completion of a structured residency/fellowship at an institution's program where no qualifying individual PD/APD is identifiable, or the era predates formal PD structure. Any era (unlike `observational_study`, which stays pre-1950).
- **Gating (anti-scope-creep):** requires (1) documented structured-program completion — not mere affiliation/employment; (2) an explicit note stating *why* no person endpoint qualifies — one of {mentorless-by-committee, pre-PD-era, director-unidentified}; (3) standard citation discipline (PMID/DOI/institutional_archive, content-match). `direct_training` remains strictly preferred whenever a qualifying PD/APD exists — `residency_at` is a fallback, never a convenience.

## Projection behavior
- **Lineage projection (person↔person):** EXCLUDED automatically — institution endpoint *and* edge_type outside `{direct_training, observational_study}`. Double-excluded and self-documenting; the exclusion becomes structural rather than a filter on a mislabeled edge.
- **Full-graph betweenness / geodesics:** INCLUDED (institutions already appear legitimately as intermediaries).

## Files to change (Claude Code, MacBook)
1. **`00_schema.json`** — add `"residency_at"` to `items.properties.edge_type.enum` (currently 8 types → 9). No other schema change.
2. **`pipeline_config.json`** — no route-map change required (routing is by module `route:` tag, not edge_type); `residency_at` edges route to their subject module like any other. Add `residency_at` to any per-route `edge_type_contract` only if a module is later restricted to it (none today).
3. **`networkx_diagnostic.py`** — one-line docstring/comment update on the lineage-projection predicate to name `residency_at` as an explicitly-excluded training-type-with-institution-endpoint. No logic change (the existing `edge_type ∈ {direct_training, observational_study}` filter already excludes it).
4. **README.md / SURGICAL_LINEAGE_ATLAS.md** — bump "8 edge types" → "9 edge types" in the schema section during the next docs pass.

## Batch 3 conversions (author after schema lands)
Convert via `reclassify` + `reverse_retarget` (source/target swap to person→institution):

| Current edge | → | New edge (`residency_at`) | Note key | Citation |
|---|---|---|---|---|
| MGH Dept → Frederick Coller (direct_training, 1912–17) | | Frederick Coller → MGH Dept | mentorless-by-committee | PMID 14036574 |
| Mayo Dept → R. Lee Clark (direct_training, 1935–39) | | R. Lee Clark → Mayo Dept | pre-PD-era | institutional_archive |
| MSK → LaSalle Leffall (direct_training, 1957–59) | | LaSalle Leffall → MSK | director-unidentified | **needs non-defective citation** (current 18481473 documents his chair, not this fellowship) |
| St. Mark's → Joseph M. Mathews (observational_study, 1877–78) | | *judgment call* | institution-source anomaly | PMID 23997672 |

**Mathews judgment call (carry into Batch 3 planning):** currently an institution-source `observational_study`, anomalous under the person↔person predicate. If the St. Mark's period (winter 1877–78) was structured study → convert to `Mathews → St. Mark's residency_at`. If it was an informal observership → it fits neither type cleanly; drop it. Lean convert; decide at Batch 3 authoring.

## Out of scope for this PR
Does not touch the V15 Batch-1 re-attributions or the Batch-2 Bucket-C deletes. Does not convert the needs-node/needs-research holds (Hart, Blakemore, Flint, Jackson, Safar, Firor) — those await interim-leadership nodes or scope rulings, not this schema.
