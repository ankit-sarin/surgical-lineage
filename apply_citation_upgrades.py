#!/usr/bin/env python3
"""Apply citation upgrade changesets to Surgical Lineage Atlas module files."""

import json
import os
import sys

BASE_DIR = "/Users/asarin/Library/CloudStorage/Dropbox/PROJECTS/@ STRIVE/2026 Surgical lineage"

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

def find_edge(edges, match_fields):
    """Find matching edge(s) by source_node, target_node, edge_type."""
    matches = []
    for i, edge in enumerate(edges):
        if (edge.get("source_node") == match_fields["source_node"] and
            edge.get("target_node") == match_fields["target_node"] and
            edge.get("edge_type") == match_fields["edge_type"]):
            matches.append((i, edge))
    return matches

def run(dry_run=True):
    # Stats
    total = 0
    applied = 0
    skipped_already = 0
    errors_not_found = 0
    verification_required_count = 0
    modules_modified = {}
    verification_edges = []

    # Cache for module data (so multiple batches stack)
    module_cache = {}

    for batch_num in range(1, 8):
        changeset_path = os.path.join(BASE_DIR, f"batch{batch_num}_changeset.json")
        if not os.path.exists(changeset_path):
            print(f"WARNING: {changeset_path} not found, skipping")
            continue

        changeset = load_json(changeset_path)
        upgrades = changeset.get("upgrades", [])

        for upgrade in upgrades:
            total += 1
            module_name = upgrade["module"]
            match_fields = upgrade["match_fields"]
            new_values = upgrade["new_values"]
            notes_append = upgrade.get("notes_append", "")
            ver_req = upgrade.get("verification_required", False)

            if ver_req:
                verification_required_count += 1
                verification_edges.append({
                    "batch": batch_num,
                    "source": match_fields["source_node"],
                    "target": match_fields["target_node"],
                    "module": module_name
                })

            # Load module if not cached
            if module_name not in module_cache:
                module_path = os.path.join(BASE_DIR, module_name)
                if not os.path.exists(module_path):
                    print(f"ERROR [batch {batch_num}]: Module file {module_name} not found")
                    errors_not_found += 1
                    continue
                module_cache[module_name] = load_json(module_path)

            edges = module_cache[module_name]
            matches = find_edge(edges, match_fields)

            if len(matches) == 0:
                print(f"ERROR [batch {batch_num}]: Edge not found: "
                      f"{match_fields['source_node']} -> {match_fields['target_node']} "
                      f"({match_fields['edge_type']}) in {module_name}")
                errors_not_found += 1
                continue

            if len(matches) > 1:
                print(f"WARNING [batch {batch_num}]: Multiple matches ({len(matches)}) for "
                      f"{match_fields['source_node']} -> {match_fields['target_node']} "
                      f"in {module_name}. Applying to first match only.")

            idx, edge = matches[0]

            # Check current evidence_type
            current_type = edge.get("evidence_type", "")
            if current_type != "institutional_archive":
                print(f"SKIP [batch {batch_num}]: Edge already has evidence_type='{current_type}' "
                      f"(not institutional_archive): "
                      f"{match_fields['source_node']} -> {match_fields['target_node']} in {module_name}")
                skipped_already += 1
                continue

            if not dry_run:
                # Apply new values
                edge["evidence_citation"] = new_values["evidence_citation"]
                edge["evidence_type"] = new_values["evidence_type"]
                edge["evidence_locator"] = new_values["evidence_locator"]

                # Append notes
                existing_notes = edge.get("notes", "")
                if existing_notes and existing_notes.strip():
                    edge["notes"] = existing_notes + " " + notes_append
                else:
                    edge["notes"] = notes_append

                module_cache[module_name][idx] = edge

            applied += 1
            modules_modified[module_name] = modules_modified.get(module_name, 0) + 1

    # Write modified modules
    if not dry_run:
        for module_name, edges in module_cache.items():
            if module_name in modules_modified:
                module_path = os.path.join(BASE_DIR, module_name)
                save_json(module_path, edges)
                print(f"  Wrote {module_path}")

    # Print summary
    mode = "DRY RUN" if dry_run else "APPLIED"
    print(f"\n=== Citation Upgrade Summary ({mode}) ===")
    print(f"Total upgrades attempted: {total}")
    print(f"Successfully {'would be ' if dry_run else ''}applied: {applied}")
    print(f"Skipped (already upgraded): {skipped_already}")
    print(f"Errors (edge not found): {errors_not_found}")
    print(f"Verification required: {verification_required_count}")
    print(f"\nModules {'to be ' if dry_run else ''}modified:")
    for mod, count in sorted(modules_modified.items()):
        print(f"  {mod}: {count} edges upgraded")

    if verification_edges:
        print(f"\nEdges requiring manual name verification:")
        for v in verification_edges:
            print(f"  [batch {v['batch']}] {v['source']} -> {v['target']} in {v['module']}")

    return errors_not_found

if __name__ == "__main__":
    print("=" * 60)
    print("PRE-FLIGHT DRY RUN")
    print("=" * 60)
    errors = run(dry_run=True)

    if errors > 0:
        print(f"\n{errors} error(s) found during dry run. Review above.")
        resp = input("Proceed anyway? (y/N): ").strip().lower()
        if resp != "y":
            print("Aborted.")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("APPLYING CHANGES")
    print("=" * 60)
    run(dry_run=False)
    print("\nDone.")
