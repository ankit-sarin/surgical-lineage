#!/usr/bin/env python3
"""V5 Expansion Merge Script for Surgical Lineage Atlas."""

import json
import re
import os
import sys
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path("/Users/asarin/Library/CloudStorage/Dropbox/PROJECTS/@ STRIVE/2026 Surgical lineage")

MODULE_FILES = [
    "01_halsted_core.json",
    "02_general_surgery_spread.json",
    "03_neurosurgery.json",
    "04_cardiothoracic_vascular.json",
    "05_urology.json",
    "06_orthopedics.json",
    "07_oncology_trials.json",
    "08_subspecialties.json",
    "09_trauma_acute_infection.json",
    "10_quality_outcomes.json",
    "11_mis_robotic.json",
    "12_governance_societies.json",
    "13_pre_halsted.json",
    "14_global_military.json",
]

EXPANSION_FILES = [
    "expansion_V5_T1-01_sabiston_training_tree.json",
    "expansion_V5_T1-02_blalock_training_tree.json",
    "expansion_V5_T1-03_plastic_surgery_bridge.json",
    "expansion_V5_T1-06_hunter_physick_bridge.json",
    "expansion_V5_T1-07_small_islands_batch.json",
    "expansion_V5_T2-01_debakey_training_tree.json",
    "expansion_V5_T2-02_wangensteen_training_tree.json",
    "expansion_V5_T2-03_rhoads_penn_lineage.json",
    "expansion_V5_T2-04_zollinger_ohio_state.json",
    "expansion_V5_T2-05_brennan_msk.json",
    "expansion_V5_T2-06_ravitch_stapler.json",
    "expansion_V5_T2-07_reemtsma_columbia.json",
    "expansion_V5_T2-08_folkman_angiogenesis.json",
    "expansion_V5_T2-09_silen_beth_israel.json",
    "expansion_V5_T2-10_kocher_nobel.json",
    "expansion_V5_T3-01_ucsf_chain.json",
    "expansion_V5_T3-02_stanford_chain.json",
    "expansion_V5_T3-03_vanderbilt_depth.json",
    "expansion_V5_T3-04_emory_depth.json",
    "expansion_V5_T3-05_michigan_succession.json",
    "expansion_V5_T3-06_hopkins_modern_succession.json",
    "expansion_V5_T3-07_mattox_ben_taub.json",
    "expansion_V5_T4-06_nyhus_hernia.json",
    "expansion_V5_T4-08_organ_urm.json",
    "expansion_V5_T4-09_hendren_mgh.json",
]

REPLACEMENT_FILE = "expansion_V5_T3-02_stanford_chain.json"


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def parse_target_module(notes):
    """Extract TARGET MODULE from notes field."""
    if not notes:
        return None, False
    match = re.search(r'TARGET MODULE:\s*(\S+?)(?:\s*\(REPLACES existing edge\))?(?:\s*$)', notes)
    if not match:
        # Try alternate pattern with REPLACES
        match = re.search(r'TARGET MODULE:\s*(\S+)', notes)
    if match:
        module = match.group(1).rstrip('"').rstrip(')')
        # Strip .json suffix if present
        if module.endswith('.json'):
            module = module[:-5]
        is_replace = 'REPLACES existing edge' in notes
        return module, is_replace
    return None, False


def strip_target_annotation(notes):
    """Remove TARGET MODULE annotation from notes."""
    if not notes:
        return notes
    # Remove everything from "TARGET MODULE:" onward
    cleaned = re.sub(r'\s*TARGET MODULE:.*$', '', notes)
    return cleaned.strip()


def is_duplicate(edge, existing_edges):
    """Check if edge is a duplicate based on source_node, target_node, edge_type."""
    for ex in existing_edges:
        if (ex.get('source_node') == edge.get('source_node') and
            ex.get('target_node') == edge.get('target_node') and
            ex.get('edge_type') == edge.get('edge_type')):
            return True
    return False


def validate_schema(data, schema):
    """Basic schema validation."""
    errors = []
    if not isinstance(data, list):
        errors.append("Root must be an array")
        return errors

    valid_edge_types = schema['items']['properties']['edge_type']['enum']
    valid_node_types = schema['items']['properties']['source_node_type']['enum']
    valid_evidence_types = schema['items']['properties']['evidence_type']['enum']
    valid_confidence = schema['items']['properties']['confidence']['enum']
    required_fields = schema['items']['required']

    for i, edge in enumerate(data):
        if not isinstance(edge, dict):
            errors.append(f"Edge {i}: not an object")
            continue
        for field in required_fields:
            if field not in edge:
                errors.append(f"Edge {i} ({edge.get('source_node','?')} -> {edge.get('target_node','?')}): missing required field '{field}'")
        if edge.get('edge_type') and edge['edge_type'] not in valid_edge_types:
            errors.append(f"Edge {i}: invalid edge_type '{edge['edge_type']}'")
        if edge.get('source_node_type') and edge['source_node_type'] not in valid_node_types:
            errors.append(f"Edge {i}: invalid source_node_type '{edge['source_node_type']}'")
        if edge.get('target_node_type') and edge['target_node_type'] not in valid_node_types:
            errors.append(f"Edge {i}: invalid target_node_type '{edge['target_node_type']}'")
        if edge.get('evidence_type') and edge['evidence_type'] not in valid_evidence_types:
            errors.append(f"Edge {i}: invalid evidence_type '{edge['evidence_type']}'")
        if edge.get('confidence') and edge['confidence'] not in valid_confidence:
            errors.append(f"Edge {i}: invalid confidence '{edge['confidence']}'")
    return errors


def main():
    os.chdir(BASE_DIR)

    # Load schema
    schema = load_json("00_schema.json")

    # Load all module files
    modules = {}
    edge_counts_before = {}
    for mf in MODULE_FILES:
        modules[mf] = load_json(mf)
        edge_counts_before[mf] = len(modules[mf])

    # Track merge stats
    edges_added = defaultdict(int)
    edges_skipped_dup = 0
    edges_replaced = 0
    warnings = []

    # Process each expansion file
    for ef in EXPANSION_FILES:
        filepath = BASE_DIR / ef
        expansion_edges = load_json(filepath)

        for edge in expansion_edges:
            notes = edge.get('notes', '')
            target_module, is_replace = parse_target_module(notes)

            if not target_module:
                warnings.append(f"WARNING: No TARGET MODULE found in {ef}, edge: {edge.get('source_node')} -> {edge.get('target_node')}")
                continue

            # Map module name to filename
            target_file = target_module + '.json'
            if target_file not in modules:
                warnings.append(f"WARNING: Unknown target module '{target_module}' in {ef}, edge: {edge.get('source_node')} -> {edge.get('target_node')}")
                continue

            # Handle replacement edge (T3-02)
            if is_replace or ef == REPLACEMENT_FILE:
                replaced = False
                for existing in modules[target_file]:
                    if (existing.get('source_node') == edge.get('source_node') and
                        existing.get('target_node') == edge.get('target_node')):
                        # Replace citation fields
                        existing['evidence_citation'] = edge['evidence_citation']
                        existing['evidence_type'] = edge['evidence_type']
                        existing['evidence_locator'] = edge['evidence_locator']
                        existing['notes'] = strip_target_annotation(edge['notes'])
                        # Remove REPLACES annotation too
                        existing['notes'] = re.sub(r'\s*\(REPLACES existing edge\)', '', existing['notes']).strip()
                        edges_replaced += 1
                        replaced = True
                        print(f"  REPLACED: {edge['source_node']} -> {edge['target_node']} in {target_file}")
                        break
                if not replaced:
                    warnings.append(f"WARNING: Replacement target not found in {target_file}: {edge['source_node']} -> {edge['target_node']}")
                continue

            # Check for duplicates
            if is_duplicate(edge, modules[target_file]):
                edges_skipped_dup += 1
                warnings.append(f"DUPLICATE SKIPPED: {edge['source_node']} -> {edge['target_node']} in {target_file} (from {ef})")
                continue

            # Clean the edge
            edge['notes'] = strip_target_annotation(notes)
            edge['module'] = target_module

            # Append
            modules[target_file].append(edge)
            edges_added[target_file] += 1

    # Save all module files
    for mf in MODULE_FILES:
        save_json(mf, modules[mf])

    # Validate against schema
    print("\n=== SCHEMA VALIDATION ===")
    all_valid = True
    for mf in MODULE_FILES:
        errors = validate_schema(modules[mf], schema)
        if errors:
            all_valid = False
            print(f"\n{mf}: {len(errors)} error(s)")
            for e in errors:
                print(f"  {e}")
        else:
            print(f"  {mf}: OK ({len(modules[mf])} edges)")
    if all_valid:
        print("\nAll module files pass schema validation.")

    # Print warnings
    if warnings:
        print("\n=== WARNINGS ===")
        for w in warnings:
            print(f"  {w}")

    # Summary table
    print("\n=== MERGE SUMMARY ===")
    print(f"{'Module File':<42} | {'Before':>7} | {'Added':>7} | {'After':>7}")
    print("-" * 72)
    total_before = 0
    total_added = 0
    total_after = 0
    for mf in MODULE_FILES:
        before = edge_counts_before[mf]
        added = edges_added[mf]
        after = len(modules[mf])
        total_before += before
        total_added += added
        total_after += after
        print(f"{mf:<42} | {before:>7} | {added:>7} | {after:>7}")
    print("-" * 72)
    print(f"{'TOTAL':<42} | {total_before:>7} | {total_added:>7} | {total_after:>7}")
    print(f"\nEdges replaced: {edges_replaced}")
    print(f"Duplicates skipped: {edges_skipped_dup}")


if __name__ == '__main__':
    main()
