#!/usr/bin/env python3
"""
Tests for the V17-T1 pipeline hardening items.

  T1.1  merge_run records carry canonical_sha256_pre / _post (full 64-hex).
  T1.2  phase_i tolerates a manifest with no manifest_id (log label only).
  T1.3  manifest pre-flight validation against 00_manifest_schema.json, which must fail
        BEFORE any module read or mutation.
  T1.4  Audit 1 reports the whitelist-filtered UNION of the fuzzy-ratio and token
        detectors, and accounts for every suppressed pair.

SAFETY: every test that runs the pipeline does so inside a pytest tmp_path sandbox — a
copy of the config, the module JSONs, the canonical and the labels. Nothing here reads
or writes the repo's real graph artifacts. The sandbox runs use an EMPTY expansion and
zero-operation manifests, so a full phase_i -> phase_h pass is a structural no-op whose
regenerated canonical is byte-identical to the copy it started from.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent
HEX64 = re.compile(r"^[0-9a-f]{64}$")


# --------------------------------------------------------------------------- sandbox
def _sandbox(tmp_path):
    """Copy the pipeline's inputs into tmp_path. Config paths resolve relative to the
    config file's own directory, so copying the config in redirects the whole run."""
    for name in ("pipeline_config.json", "00_schema.json",
                 "surgical_lineage_graph_canonical.json", "node_labels_adjudicated.json"):
        shutil.copy(BASE / name, tmp_path / name)
    for mod in sorted(BASE.glob("[0-9][0-9]_*.json")):
        if not mod.name.startswith("00_"):
            shutil.copy(mod, tmp_path / mod.name)
    if (BASE / "00_manifest_schema.json").exists():          # present from T1.3 onward
        shutil.copy(BASE / "00_manifest_schema.json", tmp_path / "00_manifest_schema.json")
    return tmp_path


def _write_noop_inputs(d, manifest_id=True):
    """An empty batch plus zero-operation manifests: a structurally inert merge."""
    (d / "exp.json").write_text("[]")
    a = {"manifest_type": "edge_modify_fields", "target_module": "13_pre_halsted.json",
         "description": "no-op", "operations": []}
    b = {"manifest_type": "edge_semantic_ops", "target_module": "13_pre_halsted.json",
         "description": "no-op", "operations": []}
    if manifest_id:
        a["manifest_id"] = "test_a"
        b["manifest_id"] = "test_b"
    (d / "man_a.json").write_text(json.dumps(a, indent=2))
    (d / "man_b.json").write_text(json.dumps(b, indent=2))
    return d / "exp.json", d / "man_a.json", d / "man_b.json"


def _run(script, *args, cwd):
    return subprocess.run([sys.executable, str(BASE / script), *map(str, args)],
                          cwd=cwd, capture_output=True, text=True)


def _phase_i(d, exp, a, b, version="test"):
    return _run("phase_i_merge.py", "--expansion", exp, "--manifest-a", a, "--manifest-b", b,
                "--version", version, "--config", d / "pipeline_config.json", cwd=d)


# --------------------------------------------------------------------------- T1.1
def test_t1_1_phase_i_writes_pre_hash_and_null_post(tmp_path):
    d = _sandbox(tmp_path)
    exp, a, b = _write_noop_inputs(d)
    r = _phase_i(d, exp, a, b)
    assert r.returncode == 0, r.stderr

    rec = json.loads((d / "merge_run_test.json").read_text())
    assert "canonical_sha256_pre" in rec and "canonical_sha256_post" in rec
    assert HEX64.match(rec["canonical_sha256_pre"]), rec["canonical_sha256_pre"]
    # Deliberate: phase_i cannot know the post hash (phase_h regenerates the canonical).
    # pre populated + post null is the signature of a run stopped between phases.
    assert rec["canonical_sha256_post"] is None


def test_t1_1_pre_hash_matches_canonical_on_disk(tmp_path):
    import hashlib
    d = _sandbox(tmp_path)
    exp, a, b = _write_noop_inputs(d)
    expected = hashlib.sha256((d / "surgical_lineage_graph_canonical.json").read_bytes()).hexdigest()
    assert _phase_i(d, exp, a, b).returncode == 0
    assert json.loads((d / "merge_run_test.json").read_text())["canonical_sha256_pre"] == expected


def test_t1_1_full_pipeline_pass_populates_both_hashes(tmp_path):
    """INTEGRATION: phase_i then phase_h — both fields 64-hex once the pipeline completes."""
    d = _sandbox(tmp_path)
    exp, a, b = _write_noop_inputs(d)
    assert _phase_i(d, exp, a, b).returncode == 0
    h = _run("phase_h_apply.py", "--version", "test",
             "--run-record", d / "merge_run_test.json",
             "--config", d / "pipeline_config.json", cwd=d)
    assert h.returncode == 0, h.stdout + h.stderr

    rec = json.loads((d / "merge_run_test.json").read_text())
    assert HEX64.match(rec["canonical_sha256_pre"]), rec["canonical_sha256_pre"]
    assert HEX64.match(rec["canonical_sha256_post"]), rec["canonical_sha256_post"]
    # This batch is a structural no-op, so the regenerated canonical must hash to the input.
    assert rec["canonical_sha256_post"] == rec["canonical_sha256_pre"]


def test_t1_1_phase_h_preserves_the_rest_of_the_record(tmp_path):
    d = _sandbox(tmp_path)
    exp, a, b = _write_noop_inputs(d)
    assert _phase_i(d, exp, a, b).returncode == 0
    before = json.loads((d / "merge_run_test.json").read_text())
    assert _run("phase_h_apply.py", "--version", "test",
                "--run-record", d / "merge_run_test.json",
                "--config", d / "pipeline_config.json", cwd=d).returncode == 0
    after = json.loads((d / "merge_run_test.json").read_text())
    assert after["canonical_sha256_pre"] == before["canonical_sha256_pre"]
    for k in ("version", "pre", "delta", "inputs", "new_nodes", "manifest_ops"):
        assert after[k] == before[k], f"phase_h mutated {k!r}"


# --------------------------------------------------------------------------- T1.2
def test_t1_2_missing_manifest_id_does_not_abort(tmp_path):
    """manifest_id is a log label. Omitting it must not KeyError (V17-B2 aborted mid-merge)."""
    d = _sandbox(tmp_path)
    exp, a, b = _write_noop_inputs(d, manifest_id=False)
    assert "manifest_id" not in json.loads(a.read_text())
    assert "manifest_id" not in json.loads(b.read_text())

    r = _phase_i(d, exp, a, b)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "KeyError" not in r.stderr
    assert "<unnamed>" in r.stdout, r.stdout
    assert (d / "merge_run_test.json").exists()


def test_t1_2_present_manifest_id_still_labels_the_phase(tmp_path):
    d = _sandbox(tmp_path)
    exp, a, b = _write_noop_inputs(d, manifest_id=True)
    r = _phase_i(d, exp, a, b)
    assert r.returncode == 0, r.stderr
    assert "test_a" in r.stdout and "test_b" in r.stdout
    assert "<unnamed>" not in r.stdout


# --------------------------------------------------------------------------- T1.3
SCHEMA_MANIFEST = json.loads((BASE / "00_manifest_schema.json").read_text())


def _match(**kw):
    m = {"source_node": "A", "target_node": "B", "edge_type": "direct_training"}
    m.update(kw)
    return m


def _bad_manifests():
    """Each fixture violates exactly one requirement derived from the phase_i code path."""
    return {
        "missing_op": {
            "manifest_type": "edge_modify_fields", "target_module": "13_pre_halsted.json",
            "operations": [{"match": _match(), "expected_existing": {"start_year": 1}, "set": {"end_year": 2}}]},
        "missing_module": {
            "manifest_type": "edge_semantic_ops",
            "operations": [{"op": "reclassify", "match": _match(),
                            "expected_existing": {"start_year": 1}, "set": {"edge_type": "x"}}]},
        "unknown_manifest_type": {"manifest_type": "edge_teleport", "operations": []},
    }


@pytest.mark.parametrize("name,doc", sorted(_bad_manifests().items()))
def test_t1_3_negative_fixtures_fail_schema(name, doc):
    import jsonschema
    errs = list(jsonschema.Draft7Validator(SCHEMA_MANIFEST).iter_errors(doc))
    assert errs, f"{name} should have failed validation"


def test_t1_3_live_v17_b2_manifests_validate_clean():
    """GATE 3 — the manifests actually merged in V17-B2 must pass the new pre-flight."""
    import jsonschema
    v = jsonschema.Draft7Validator(SCHEMA_MANIFEST)
    for f in ("v17_b2_manifest_a.json", "v17_b2_manifest_b.json"):
        assert list(v.iter_errors(json.loads((BASE / f).read_text()))) == [], f


def test_t1_3_delete_needs_no_set_but_reclassify_does():
    """op_delete never reads op['set']; op_reverse_retarget and op_reclassify both do."""
    import jsonschema
    v = jsonschema.Draft7Validator(SCHEMA_MANIFEST)
    base_op = {"module": "m.json", "match": _match(), "expected_existing": {"start_year": 1}}
    ok = {"manifest_type": "edge_semantic_ops", "operations": [{"op": "delete", **base_op}]}
    bad = {"manifest_type": "edge_semantic_ops", "operations": [{"op": "reclassify", **base_op}]}
    assert list(v.iter_errors(ok)) == []
    assert [e.message for e in v.iter_errors(bad)]


@pytest.mark.parametrize("name", sorted(_bad_manifests()))
def test_t1_3_phase_i_aborts_before_touching_any_module(tmp_path, name):
    """GATE 2 — a bad manifest must fail pre-flight with a clear message, provably BEFORE
    any module is mutated. The expansion here is non-empty, so a run that got as far as the
    batch insert would rewrite module 13 and emit a run record."""
    d = _sandbox(tmp_path)
    exp, a, b = _write_noop_inputs(d)
    exp.write_text(json.dumps([{
        "source_node": "T1.3 Probe", "source_node_type": "person",
        "target_node": "T1.3 Target", "target_node_type": "person",
        "edge_type": "direct_training", "start_year": 1900, "end_year": 1901,
        "temporal_range": "1900-1901", "evidence_citation": "none", "evidence_type": "PMID",
        "evidence_locator": "none", "confidence": "high", "notes": "route: 13_pre_halsted"}]))
    doc = _bad_manifests()[name]
    # Break Manifest B for the semantic fixture, Manifest A otherwise.
    (b if doc["manifest_type"] == "edge_semantic_ops" else a).write_text(json.dumps(doc, indent=2))

    before = (d / "13_pre_halsted.json").read_bytes()
    r = _phase_i(d, exp, a, b)

    assert r.returncode != 0, "bad manifest must abort"
    assert "FAILED" in r.stdout and "no module was read or modified" in r.stdout
    assert (d / "13_pre_halsted.json").read_bytes() == before, "module was mutated despite abort"
    assert not (d / "merge_run_test.json").exists(), "run record emitted despite abort"
    assert "Phase I.1" not in r.stdout, "batch insert ran despite a failed pre-flight"


def test_t1_3_valid_manifests_pass_preflight_and_run(tmp_path):
    d = _sandbox(tmp_path)
    exp, a, b = _write_noop_inputs(d)
    r = _phase_i(d, exp, a, b)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Phase I.0 — manifest pre-flight" in r.stdout
    assert r.stdout.count("validates against") == 2


# --------------------------------------------------------------------------- T1.4
import diagnostic_audit as da

CANONICAL = json.loads((BASE / "surgical_lineage_graph_canonical.json").read_text())
TOKEN_PAIR = ("Joseph M. Mathews", "Joseph McDowell Mathews")   # token-only: ratio 0.80 < 0.88


def _nodes(*names, ntype="person"):
    return {(n, ntype): {"01"} for n in names}


def test_t1_4_token_only_pair_is_reported_and_tagged():
    """The token detector must reach Audit 1's output — the fuzzy gate alone misses this pair."""
    a, b = TOKEN_PAIR
    from difflib import SequenceMatcher
    assert SequenceMatcher(None, a, b).ratio() < da.PERSON_SIM_THRESHOLD    # fuzzy cannot see it
    assert da.person_name_variant(a, b)                                     # token can

    lines, stats = da.audit_1_canonical_names(_nodes(a, b), {})
    assert stats["person_pairs"] == 1
    assert stats["person_pairs_by_detector"] == {"token": 1}
    assert any("token" in ln and a in ln for ln in lines)


def test_t1_4_whitelisted_token_pair_is_suppressed_but_counted():
    """The T1.4 defect: a whitelisted token hit used to be dropped silently, so the
    'Whitelisted name pairs' counter under-reported it."""
    a, b = TOKEN_PAIR
    lines, stats = da.audit_1_canonical_names(_nodes(a, b), {frozenset({a, b}): "distinct people"})
    assert stats["person_pairs"] == 0, "whitelisted pair must not be flagged"
    assert stats["suppressed"] == 1, "whitelisted pair must still be COUNTED"
    assert stats["suppressed_by_detector"] == {"token": 1}
    assert any("[detector: token; whitelisted]" in ln for ln in lines)


def test_t1_4_whitelisted_fuzzy_pair_still_suppressed_and_tagged():
    a, b = "ACS National Surgical Quality Improvement Program", \
           "VA National Surgical Quality Improvement Program"
    lines, stats = da.audit_1_canonical_names(_nodes(a, b, ntype="institution"),
                                              {frozenset({a, b}): "distinct programs"})
    assert stats["suppressed"] == 1
    assert stats["suppressed_by_detector"] == {"fuzzy": 1}
    assert any("[detector: fuzzy; whitelisted]" in ln for ln in lines)


def test_t1_4_pair_seen_by_both_detectors_is_one_row_with_both_tags():
    # Present-vs-absent middle initial: high ratio AND a token variant. (Two DIFFERING middle
    # initials would not qualify — the token rule deliberately treats those as distinct people,
    # per test_v16_pr.py::test_differing_middle_initials_no_flag.)
    a, b = "William Halsted", "William S. Halsted"
    from difflib import SequenceMatcher
    assert SequenceMatcher(None, a, b).ratio() >= da.PERSON_SIM_THRESHOLD
    assert da.person_name_variant(a, b)
    _, stats = da.audit_1_canonical_names(_nodes(a, b), {})
    assert stats["person_pairs"] == 1, "must not be double-counted"
    assert list(stats["person_pairs_by_detector"]) == ["fuzzy+token"]


def test_t1_4_token_path_is_exercised_on_the_live_canonical():
    """End-to-end through the audit on real data: the whitelisted Warren pair is the
    token detector's only live hit, and it must now appear tagged and counted."""
    node_modules = {}
    for e in CANONICAL:
        for k in ("source_node", "target_node"):
            node_modules.setdefault((e[k], e[f"{'source' if k == 'source_node' else 'target'}_node_type"]),
                                    set()).add("canonical")
    whitelist = {frozenset(entry["pair"]): entry.get("reason", "")
                 for entry in json.loads((BASE / "pipeline_config.json").read_text())["name_pair_whitelist"]}

    lines, stats = da.audit_1_canonical_names(node_modules, whitelist)
    assert stats["person_pairs"] == 0, "no UNSUPPRESSED person flags expected at this graph state"
    assert stats["suppressed_by_detector"].get("token", 0) >= 1, "token suppression must be counted"
    assert any("John Warren" in ln and "[detector: token; whitelisted]" in ln for ln in lines)


def test_t1_4_is_warn_level_and_creates_no_blocking_class():
    """Audit 1 must not gain a blocking gate: flagged and suppressed pairs are context only."""
    a, b = TOKEN_PAIR
    lines, stats = da.audit_1_canonical_names(_nodes(a, b), {})
    assert stats["person_pairs"] == 1
    assert not any("BLOCKING" in ln for ln in lines)
    assert all(k in ("person_pairs", "institution_pairs", "society_pairs",
                     "institution_high_ratio", "suppressed",
                     "person_pairs_by_detector", "suppressed_by_detector") for k in stats)
