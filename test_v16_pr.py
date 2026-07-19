#!/usr/bin/env python3
"""
Tests for V16-PR — residency_at schema (v3.1) + diagnostic_audit hardening.

Covers the three TESTS REQUIRED by the task spec:
  1. residency_at [residency_at_reason: X] token gate (valid / missing / duplicate / off-list),
  2. hardened person-name variant heuristic (Mathews flag; surname/suffix negatives),
  3. schema validation (residency_at accepted; fabricated 10th type rejected).
"""
import json
from pathlib import Path

import jsonschema
import pytest

import diagnostic_audit as da

BASE = Path(__file__).resolve().parent
SCHEMA = json.loads((BASE / "00_schema.json").read_text())
CANONICAL = json.loads((BASE / "surgical_lineage_graph_canonical.json").read_text())


def _residency_edge(notes, edge_type="residency_at"):
    return {
        "source_node": "Frederick Coller", "source_node_type": "person",
        "target_node": "Massachusetts General Hospital Department of Surgery",
        "target_node_type": "institution",
        "edge_type": edge_type,
        "start_year": 1912, "end_year": 1917, "temporal_range": "1912-1917",
        "evidence_citation": "PMID: 14036574", "evidence_type": "PMID",
        "evidence_locator": "https://pubmed.ncbi.nlm.nih.gov/14036574/",
        "confidence": "high", "notes": notes,
    }


# ---------------------------------------------------------------- Test 1: token gate
@pytest.mark.parametrize("reason", sorted(da.RESIDENCY_REASONS))
def test_residency_valid_token_no_finding(reason):
    e = _residency_edge(f"Structured program completion. [residency_at_reason: {reason}] "
                        f"direct_training-first search returned no PD.")
    assert da.residency_token_finding(e) is None


def test_residency_missing_token_is_blocking():
    e = _residency_edge("Structured residency but no machine-checkable reason token present.")
    assert da.residency_token_finding(e) is not None


def test_residency_duplicate_token_is_blocking():
    e = _residency_edge("[residency_at_reason: pre-PD-era] ... [residency_at_reason: pre-PD-era]")
    finding = da.residency_token_finding(e)
    assert finding is not None and "2" in finding


def test_residency_offlist_reason_is_blocking():
    e = _residency_edge("[residency_at_reason: because-committee-said-so]")
    finding = da.residency_token_finding(e)
    assert finding is not None and "off-list" in finding


def test_non_residency_edge_is_never_checked():
    e = _residency_edge("no token at all", edge_type="direct_training")
    assert da.residency_token_finding(e) is None


# ---------------------------------------------------------------- Test 2: name heuristic
def test_mathews_middle_variant_flags():
    assert da.person_name_variant("Joseph M. Mathews", "Joseph McDowell Mathews") is True


def test_differing_surname_never_flags():
    assert da.person_name_variant("George C. Lewis Jr.", "George C. Morris Jr.") is False


def test_suffix_present_vs_absent_no_flag():
    assert da.person_name_variant("John Doe Jr.", "John Doe") is False


def test_identical_strings_not_a_pair():
    assert da.person_name_variant("Joseph McDowell Mathews", "Joseph McDowell Mathews") is False


def test_present_vs_absent_middle_flags():
    assert da.person_name_variant("Joseph Mathews", "Joseph McDowell Mathews") is True


def test_differing_middle_initials_no_flag():
    # Same first/last but genuinely different middle initials => different people, no flag.
    assert da.person_name_variant("Joseph A. Mathews", "Joseph B. Mathews") is False


def test_canonical_person_sweep_flags_exactly_mathews():
    persons = sorted({e[k] for e in CANONICAL for k in ("source_node", "target_node")
                      if e[f"{'source' if k=='source_node' else 'target'}_node_type"] == "person"})
    variants = da.structural_person_variants(persons)
    assert variants == [("Joseph M. Mathews", "Joseph McDowell Mathews")]


# ---------------------------------------------------------------- Test 3: schema
def test_schema_accepts_residency_at():
    jsonschema.validate([_residency_edge("[residency_at_reason: mentorless-by-committee]")], SCHEMA)


def test_schema_rejects_fabricated_tenth_type():
    edge = _residency_edge("x")
    edge["edge_type"] = "fabricated_tenth_type"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate([edge], SCHEMA)


def _rejected_indices(schema):
    """Indices of canonical edges that fail item-level validation under `schema`."""
    validator = jsonschema.Draft7Validator(schema["items"])
    return {i for i, e in enumerate(CANONICAL) if not validator.is_valid(e)}


# v3 schema = v3.1 minus residency_at (the only edit to the edge_type enum).
V3_SCHEMA = json.loads(json.dumps(SCHEMA))
V3_SCHEMA["items"]["properties"]["edge_type"]["enum"] = [
    t for t in V3_SCHEMA["items"]["properties"]["edge_type"]["enum"] if t != "residency_at"
]


def test_enum_change_rejects_nothing_new():
    # Gate 1 (backward-compat): adding residency_at rejects no edge that v3 accepted.
    # The only rejections are 7 PRE-EXISTING null-end_year "Present" edges, identical under both.
    assert _rejected_indices(SCHEMA) == _rejected_indices(V3_SCHEMA)


def test_all_existing_edge_types_are_valid_enum_members():
    enum = set(SCHEMA["items"]["properties"]["edge_type"]["enum"])
    assert {e["edge_type"] for e in CANONICAL} <= enum


def test_integer_year_edges_all_validate():
    # Every edge whose years are proper integers validates under v3.1 (isolates the enum edit
    # from the pre-existing null-end_year data issue, which is out of scope for this PR).
    validator = jsonschema.Draft7Validator(SCHEMA["items"])
    for e in CANONICAL:
        if isinstance(e.get("start_year"), int) and isinstance(e.get("end_year"), int):
            assert validator.is_valid(e), (e["source_node"], e["target_node"])


def test_schema_has_nine_edge_types():
    enum = SCHEMA["items"]["properties"]["edge_type"]["enum"]
    assert "residency_at" in enum and len(enum) == 9
