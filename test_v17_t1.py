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
