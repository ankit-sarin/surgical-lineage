#!/usr/bin/env python3
"""Post-merge statistics for Surgical Lineage Atlas V5."""

import json
from pathlib import Path
from collections import defaultdict, deque

BASE_DIR = Path("/Users/asarin/Library/CloudStorage/Dropbox/PROJECTS/@ STRIVE/2026 Surgical lineage")

MODULE_FILES = [
    "01_halsted_core.json", "02_general_surgery_spread.json", "03_neurosurgery.json",
    "04_cardiothoracic_vascular.json", "05_urology.json", "06_orthopedics.json",
    "07_oncology_trials.json", "08_subspecialties.json", "09_trauma_acute_infection.json",
    "10_quality_outcomes.json", "11_mis_robotic.json", "12_governance_societies.json",
    "13_pre_halsted.json", "14_global_military.json",
]


def load_all_edges():
    all_edges = []
    for mf in MODULE_FILES:
        edges = json.load(open(BASE_DIR / mf))
        all_edges.extend(edges)
    return all_edges


def compute_stats(edges):
    print("=== POST-MERGE STATISTICS ===\n")

    # 1. Total edges
    print(f"1. Total edges across all 14 modules: {len(edges)}")

    # 2. Total unique nodes
    nodes = set()
    for e in edges:
        nodes.add(e['source_node'])
        nodes.add(e['target_node'])
    print(f"2. Total unique nodes: {len(nodes)}")

    # 3. Citation rate
    cited = sum(1 for e in edges if e.get('evidence_type') in ('PMID', 'DOI'))
    rate = cited / len(edges) * 100 if edges else 0
    print(f"3. Citation rate (PMID or DOI): {cited}/{len(edges)} = {rate:.1f}%")

    # 4. Connected components (undirected)
    adj = defaultdict(set)
    for e in edges:
        s, t = e['source_node'], e['target_node']
        adj[s].add(t)
        adj[t].add(s)

    visited = set()
    components = []

    for node in nodes:
        if node not in visited:
            # BFS
            component = []
            queue = deque([node])
            while queue:
                n = queue.popleft()
                if n in visited:
                    continue
                visited.add(n)
                component.append(n)
                for neighbor in adj[n]:
                    if neighbor not in visited:
                        queue.append(neighbor)
            components.append(component)

    components.sort(key=len, reverse=True)
    print(f"\n4. Connected components: {len(components)}")
    for i, comp in enumerate(components):
        if len(comp) <= 10:
            print(f"   Component {i+1} ({len(comp)} nodes): {', '.join(sorted(comp))}")
        else:
            print(f"   Component {i+1}: {len(comp)} nodes")

    # 5. Top 10 nodes by degree
    degree = defaultdict(int)
    for e in edges:
        degree[e['source_node']] += 1
        degree[e['target_node']] += 1

    top10 = sorted(degree.items(), key=lambda x: -x[1])[:10]
    print(f"\n5. Top 10 nodes by degree (in + out):")
    print(f"   {'Node':<55} | Degree")
    print(f"   {'-'*55}-+-------")
    for node, deg in top10:
        print(f"   {node:<55} | {deg}")

    # 6. Deepest training chain (longest path using only direct_training edges)
    # Build a directed graph of direct_training edges
    training_adj = defaultdict(list)
    training_nodes = set()
    for e in edges:
        if e['edge_type'] == 'direct_training':
            training_adj[e['source_node']].append(e['target_node'])
            training_nodes.add(e['source_node'])
            training_nodes.add(e['target_node'])

    # Find all source nodes (those with no incoming training edges)
    has_incoming = set()
    for e in edges:
        if e['edge_type'] == 'direct_training':
            has_incoming.add(e['target_node'])

    roots = training_nodes - has_incoming

    # DFS to find longest path from any root
    best_path = []

    def dfs(node, path, visited):
        nonlocal best_path
        if len(path) > len(best_path):
            best_path = list(path)
        for child in training_adj[node]:
            if child not in visited:
                visited.add(child)
                path.append(child)
                dfs(child, path, visited)
                path.pop()
                visited.remove(child)

    # Also try from all nodes (in case of cycles or non-root starts)
    for root in training_nodes:
        dfs(root, [root], {root})

    print(f"\n6. Deepest training chain ({len(best_path)} generations, {len(best_path)-1} edges):")
    for i, node in enumerate(best_path):
        prefix = "   " + "  " * i
        arrow = "-> " if i > 0 else "   "
        print(f"{prefix}{arrow}{node}")

    # Print as linear chain
    print(f"\n   Chain: {' -> '.join(best_path)}")

    return len(edges), len(nodes)


if __name__ == '__main__':
    edges = load_all_edges()
    compute_stats(edges)
