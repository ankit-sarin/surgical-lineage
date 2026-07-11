#!/usr/bin/env python3
"""
Tests for the phase_g_labels.py reconcile path (append + prune + loud reporting +
mass-prune guard). All tests run against in-memory fixtures or temp-dir copies — they
NEVER read or mutate the live label / canonical / module files.

Numbered per the V15-PHASEG-PRUNE contract:
  1. append-only     -> N appended, 0 pruned, parity holds
  2. prune-only      -> 0 appended, M pruned (itemized), parity holds (V15-B2 model)
  3. mixed           -> both lists reported, parity holds
  4. no-op           -> 0/0, parity holds, idempotent on a second run
  5. mass-prune guard-> prune count over --max-prune ABORTS, label file left unmodified
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

import phase_g_labels as pg


# --------------------------------------------------------------------------- helpers
def lbl(nid, ntype="person", degree=1, **overrides):
    entry = {
        "id": nid,
        "type": ntype,
        "degree": degree,
        "label_short": "",
        "label_short_source": "stub_pending_adjudication",
        "reviewed": False,
    }
    entry.update(overrides)
    return entry


def canon(ids, ntype="person", degree=1):
    return {i: (ntype, degree) for i in ids}


def write_graph(tmp, node_ids, labels):
    """Materialize a temp pipeline: one numbered module whose node set == node_ids,
    a labels.json, and a config pointing at both. Returns (config_path, labels_path)."""
    tmp = Path(tmp)
    ids = list(node_ids)
    # Star topology from ids[0] so the module's node set is exactly `node_ids`.
    edges = []
    hub = ids[0]
    for other in ids[1:]:
        edges.append({
            "source_node": hub, "source_node_type": "person",
            "target_node": other, "target_node_type": "person",
            "edge_type": "direct_training",
        })
    if len(ids) == 1:  # single-node graph: self-referencing degenerate edge keeps the node present
        edges.append({
            "source_node": hub, "source_node_type": "person",
            "target_node": hub, "target_node_type": "person",
            "edge_type": "direct_training",
        })
    (tmp / "01_test_module.json").write_text(json.dumps(edges, indent=2))
    labels_path = tmp / "labels.json"
    labels_path.write_text(json.dumps(labels, indent=2))
    config_path = tmp / "pipeline_config.json"
    config_path.write_text(json.dumps({
        "paths": {"modules_dir": ".", "node_labels": "labels.json"}
    }, indent=2))
    return config_path, labels_path


def run_main(config_path, max_prune=10):
    """Invoke phase_g_labels.py as a subprocess (exercises main() + file I/O)."""
    return subprocess.run(
        [sys.executable, str(Path(__file__).parent / "phase_g_labels.py"),
         "--config", str(config_path), "--max-prune", str(max_prune)],
        capture_output=True, text=True,
    )


# --------------------------------------------------------------------------- 1. append-only
def test_1_append_only():
    labels = [lbl("A"), lbl("B")]
    canonical = canon(["A", "B", "C", "D"])
    reconciled, appended, pruned = pg.reconcile_labels(labels, canonical)

    assert appended == ["C", "D"]
    assert pruned == []
    assert len(reconciled) == len(canonical) == 4          # parity
    assert {e["id"] for e in reconciled} == set(canonical)
    # retained originals preserved untouched, in original order, at the front
    assert reconciled[0] == lbl("A") and reconciled[1] == lbl("B")
    # appended entries are stubs
    stub = next(e for e in reconciled if e["id"] == "C")
    assert stub["label_short"] == "" and stub["reviewed"] is False
    assert stub["label_short_source"] == pg.STUB_LABEL_SHORT_SOURCE


# --------------------------------------------------------------------------- 2. prune-only (V15-B2)
def test_2_prune_only_v15b2():
    # Model the real V15-B2 case: 430 labels -> 428 nodes, 2 orphans pruned.
    node_ids = [f"N{i:03d}" for i in range(428)]
    orphans = ["John Wennberg",
               "The Dartmouth Institute for Health Policy and Clinical Practice"]
    labels = [lbl(n) for n in node_ids] + [
        lbl("John Wennberg"),
        lbl("The Dartmouth Institute for Health Policy and Clinical Practice",
            ntype="institution"),
    ]
    assert len(labels) == 430
    canonical = canon(node_ids)

    reconciled, appended, pruned = pg.reconcile_labels(labels, canonical)
    assert appended == []
    assert sorted(e["id"] for e in pruned) == sorted(orphans)     # itemized by name
    assert len(reconciled) == len(canonical) == 428               # 428 == 428 parity
    assert {e["id"] for e in reconciled} == set(node_ids)


def test_2b_prune_only_main_reports_by_name(tmp_path):
    """Same case through main() I/O: names printed, parity PASS, file reconciled."""
    node_ids = [f"N{i:03d}" for i in range(6)]
    labels = [lbl(n) for n in node_ids] + [
        lbl("John Wennberg"),
        lbl("The Dartmouth Institute for Health Policy and Clinical Practice",
            ntype="institution"),
    ]
    config_path, labels_path = write_graph(tmp_path, node_ids, labels)
    res = run_main(config_path)

    assert res.returncode == 0, res.stderr
    assert "Pruned labels (2):" in res.stdout
    assert "John Wennberg" in res.stdout
    assert "The Dartmouth Institute for Health Policy and Clinical Practice" in res.stdout
    assert "Phase G validation: PASS" in res.stdout
    # file now reconciled to exactly the node set
    final = json.loads(labels_path.read_text())
    assert {e["id"] for e in final} == set(node_ids)


# --------------------------------------------------------------------------- 3. mixed
def test_3_mixed_add_and_remove():
    labels = [lbl("A"), lbl("B"), lbl("STALE")]
    canonical = canon(["A", "B", "C"])            # +C, -STALE
    reconciled, appended, pruned = pg.reconcile_labels(labels, canonical)

    assert appended == ["C"]
    assert [e["id"] for e in pruned] == ["STALE"]
    assert len(reconciled) == len(canonical) == 3
    assert {e["id"] for e in reconciled} == {"A", "B", "C"}


# --------------------------------------------------------------------------- 4. no-op / idempotent
def test_4_noop_idempotent():
    labels = [lbl("A"), lbl("B")]
    canonical = canon(["A", "B"])

    r1, ap1, pr1 = pg.reconcile_labels(labels, canonical)
    assert ap1 == [] and pr1 == []
    assert len(r1) == len(canonical) == 2

    # second consecutive run on the reconciled output: still 0/0, same ids/order
    r2, ap2, pr2 = pg.reconcile_labels(r1, canonical)
    assert ap2 == [] and pr2 == []
    assert [e["id"] for e in r2] == [e["id"] for e in r1]


def test_4b_noop_main_is_byte_stable(tmp_path):
    """main() on an already-correct label file writes byte-identical output twice."""
    node_ids = [f"N{i}" for i in range(5)]
    labels = [lbl(n) for n in node_ids]
    config_path, labels_path = write_graph(tmp_path, node_ids, labels)

    res1 = run_main(config_path)
    assert res1.returncode == 0, res1.stderr
    assert "Entries appended: 0 | entries pruned: 0" in res1.stdout
    bytes1 = labels_path.read_bytes()

    res2 = run_main(config_path)
    assert res2.returncode == 0, res2.stderr
    assert "Entries appended: 0 | entries pruned: 0" in res2.stdout
    bytes2 = labels_path.read_bytes()

    assert bytes1 == bytes2  # idempotent + byte-stable


# --------------------------------------------------------------------------- 5. mass-prune guard
def test_5_massprune_guard_raises():
    canonical = canon(["A"])
    labels = [lbl("A")] + [lbl(f"orphan{i}") for i in range(11)]   # 11 orphans
    with pytest.raises(pg.MassPruneError) as ei:
        pg.reconcile_labels(labels, canonical, max_prune=10)
    assert len(ei.value.to_prune) == 11
    assert ei.value.max_prune == 10

    # boundary: exactly max_prune orphans does NOT trip the rail
    labels10 = [lbl("A")] + [lbl(f"orphan{i}") for i in range(10)]
    reconciled, appended, pruned = pg.reconcile_labels(labels10, canonical, max_prune=10)
    assert len(pruned) == 10 and appended == []
    assert len(reconciled) == 1


def test_5b_massprune_leaves_file_unmodified(tmp_path):
    """Over-threshold prune through main(): exit non-zero, itemized list, file untouched."""
    node_ids = ["A"]
    labels = [lbl("A")] + [lbl(f"orphan{i}", ntype="institution") for i in range(11)]
    config_path, labels_path = write_graph(tmp_path, node_ids, labels)
    before = labels_path.read_bytes()

    res = run_main(config_path, max_prune=10)

    assert res.returncode == 2
    assert "ABORT" in res.stdout and "mass-prune guard" in res.stdout
    assert "orphan0" in res.stdout                       # itemized
    assert labels_path.read_bytes() == before            # file left unmodified


# --------------------------------------------------------------------------- integrity guard
def test_retained_entry_never_modified(tmp_path):
    """A pre-existing entry with real adjudicated content survives a mixed run unchanged."""
    node_ids = ["Keep1", "Keep2"]
    labels = [
        lbl("Keep1", ntype="institution", degree=7,
            label_short="MSK", label_short_source="v14_task", reviewed=True),
        lbl("Keep2"),
        lbl("Gone"),                                     # will be pruned
    ]
    config_path, labels_path = write_graph(tmp_path, node_ids, labels)
    res = run_main(config_path)
    assert res.returncode == 0, res.stderr
    final = {e["id"]: e for e in json.loads(labels_path.read_text())}
    assert final["Keep1"]["label_short"] == "MSK"
    assert final["Keep1"]["reviewed"] is True
    assert "Gone" not in final
