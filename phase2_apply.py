#!/usr/bin/env python3
"""
Phase 2: Apply Adjudicated Citation Repairs

Reads citation_repair_candidates.json with populated action fields,
applies all 111 decisions to module files, re-verifies new PMIDs/DOIs,
regenerates canonical graph, and produces Phase 2 report.
"""

import json
import glob
import os
import re
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter, OrderedDict

BASE = "/Users/asarin/Library/CloudStorage/Dropbox/PROJECTS/@ STRIVE/2026 Surgical lineage"
ADJUDICATION = os.path.join(BASE, "citation_repair_candidates.json")
CANONICAL = os.path.join(BASE, "surgical_lineage_graph_canonical.json")
REPORT_OUT = os.path.join(BASE, "verification_report_phase2.json")
DELETED_OUT = os.path.join(BASE, "archive", "phase2_deleted_edges.json")

NCBI_DELAY = 0.35
CROSSREF_DELAY = 0.5

# Key order for edges (preserve original ordering)
EDGE_KEYS = [
    'source_node', 'source_node_type', 'target_node', 'target_node_type',
    'edge_type', 'start_year', 'end_year', 'temporal_range',
    'evidence_citation', 'evidence_type', 'evidence_locator',
    'confidence', 'notes'
]

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')

def ordered_edge(edge):
    """Return edge dict with keys in canonical order."""
    result = OrderedDict()
    for k in EDGE_KEYS:
        if k in edge:
            result[k] = edge[k]
    # Any extra keys we didn't expect
    for k in edge:
        if k not in result:
            result[k] = edge[k]
    return dict(result)

def module_files():
    pattern = os.path.join(BASE, "[0-1][0-9]_*.json")
    files = sorted(glob.glob(pattern))
    return [f for f in files if not os.path.basename(f).startswith("00_")]

def strip_verification_stamps(notes):
    """Remove Phase 1/1.5 verification stamps from notes."""
    # Remove [Verified ...] stamps (with all inner content including pipe-separated sections)
    notes = re.sub(r'\[Verified [^\]]*\]\s*', '', notes)
    # Remove [VERIFY_FAILED ...] stamps
    notes = re.sub(r'\[VERIFY_FAILED[^\]]*\]\s*', '', notes)
    return notes.strip()

def extract_surname(full_name):
    """Extract primary surname from a full name."""
    parts = full_name.split()
    suffixes = {'jr.', 'jr', 'sr.', 'sr', 'ii', 'iii', 'iv', 'md', 'phd'}
    clean = [p for p in parts if p.lower().rstrip('.') not in suffixes]
    if clean:
        return clean[-1].rstrip('.')
    return parts[-1].rstrip('.') if parts else "Unknown"

def build_archive_citation(edge, notes):
    """Build an institutional_archive citation string from edge context."""
    source = edge.get('source_node', '')
    target = edge.get('target_node', '')
    source_type = edge.get('source_node_type', '')
    target_type = edge.get('target_node_type', '')

    # Determine the institution and person
    if target_type == 'institution':
        inst = target
        person_surname = extract_surname(source) if source_type == 'person' else ''
    elif source_type == 'institution':
        inst = source
        person_surname = extract_surname(target) if target_type == 'person' else ''
    else:
        # Both persons — try to find institution from notes
        inst_match = re.search(r'(Hopkins|Duke|Stanford|Harvard|Yale|Penn|Vanderbilt|Baylor|Mayo|Columbia|Michigan|UCSF|Pittsburgh|Cleveland|Iowa|Illinois|Minnesota)', notes)
        inst = inst_match.group(1) if inst_match else 'Historical'
        person_surname = extract_surname(target)

    # Shorten institution name for citation key
    inst_short = inst.split()[0] if inst else 'Archive'
    # Remove common prefixes
    for prefix in ['Johns', 'University', 'The', 'American', 'National']:
        if inst_short == prefix and len(inst.split()) > 1:
            inst_short = inst.split()[1]

    citation = f"{inst_short}_Archive_{person_surname}" if person_surname else f"{inst_short}_Archive"
    return citation

def build_archive_locator(edge, notes):
    """Build a descriptive locator for archived edges."""
    source = edge.get('source_node', '')
    target = edge.get('target_node', '')
    source_type = edge.get('source_node_type', '')
    target_type = edge.get('target_node_type', '')

    if target_type == 'institution':
        return f"{target} Historical Records"
    elif source_type == 'institution':
        return f"{source} Historical Records"
    else:
        # Find institution context
        inst_match = re.search(r'(Johns Hopkins|Duke|Stanford|Harvard|Yale|Penn|Vanderbilt|Baylor|Mayo|Columbia|Michigan|UCSF|Pittsburgh|Cleveland Clinic|Iowa|Illinois|Minnesota|Memorial Sloan|Brigham)', notes)
        if inst_match:
            return f"{inst_match.group(1)} Department of Surgery Historical Records"
        return "Institutional historical records; biographical sources"

# ---------- Re-verification ----------

def efetch_batch(pmids):
    """Fetch article metadata for a batch of PMIDs."""
    results = {}
    if not pmids:
        return results
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": ",".join(pmids), "rettype": "xml", "retmode": "xml"}
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(full_url, headers={"User-Agent": "SurgicalLineageValidator/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_data = resp.read().decode('utf-8')
        root = ET.fromstring(xml_data)
    except Exception as e:
        print(f"    efetch error: {e}")
        return results

    for article in root.findall('.//PubmedArticle'):
        pmid_el = article.find('.//PMID')
        if pmid_el is None:
            continue
        pmid = pmid_el.text
        title_el = article.find('.//ArticleTitle')
        title = ''.join(title_el.itertext()) if title_el is not None else ""
        abstract_parts = []
        for abs_el in article.findall('.//AbstractText'):
            text = ''.join(abs_el.itertext())
            if text:
                abstract_parts.append(text)
        abstract = ' '.join(abstract_parts)
        journal_el = article.find('.//MedlineTA')
        journal = journal_el.text if journal_el is not None else ""
        year = ""
        year_el = article.find('.//PubDate/Year')
        if year_el is not None:
            year = year_el.text
        else:
            md = article.find('.//PubDate/MedlineDate')
            if md is not None and md.text:
                m = re.search(r'(\d{4})', md.text)
                if m:
                    year = m.group(1)
        authors = []
        for author in article.findall('.//Author'):
            last = author.find('LastName')
            if last is not None and last.text:
                authors.append(last.text)
        results[pmid] = {"title": title, "abstract": abstract, "journal": journal, "year": year, "authors": authors}
    return results

def fetch_crossref(doi):
    """Fetch metadata for a single DOI from CrossRef."""
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "SurgicalLineageValidator/1.0 (mailto:research@digitalsurgeon.dev)"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"    CrossRef error for {doi}: {e}")
        return None
    msg = data.get("message", {})
    title_list = msg.get("title", [])
    title = title_list[0] if title_list else ""
    abstract = re.sub(r'<[^>]+>', '', msg.get("abstract", ""))
    container = msg.get("container-title", [])
    journal = container[0] if container else ""
    year = ""
    issued = msg.get("issued", {})
    parts = issued.get("date-parts", [[]])
    if parts and parts[0]:
        year = str(parts[0][0])
    authors = [a.get("family", "") for a in msg.get("author", []) if a.get("family")]
    return {"title": title, "abstract": abstract, "journal": journal, "year": year, "authors": authors}

def build_edge_tokens(edge):
    """Extract match tokens from edge metadata."""
    tokens = set()
    for field in ['source_node', 'target_node']:
        name = edge.get(field, '')
        tokens.add(name.lower())
        for part in name.split():
            clean = part.lower().rstrip('.')
            if len(clean) > 2:
                tokens.add(clean)
    notes = edge.get('notes', '')
    notes_clean = re.sub(r'\[Phase2[^\]]*\]\s*', '', notes)
    notes_clean = re.sub(r'\[Verified[^\]]*\]\s*', '', notes_clean)
    notes_excerpt = notes_clean[:200]
    for word in notes_excerpt.split():
        clean = word.lower().strip('.,;:()[]"\'-')
        if len(clean) > 4:
            tokens.add(clean)
    return tokens

def score_match(edge_tokens, article):
    """Compute content-match score."""
    searchable = ' '.join([
        article.get('title', ''),
        article.get('abstract', ''),
        ' '.join(article.get('authors', []))
    ]).lower()
    matches = 0
    checked = 0
    for token in edge_tokens:
        if len(token) > 2:
            checked += 1
            if token in searchable:
                matches += 1
    return matches / max(checked, 1)

# ---------- Main ----------

def main():
    print("=" * 60)
    print("Phase 2: Apply Adjudicated Citation Repairs")
    print("=" * 60)

    # Load adjudication
    adj = load_json(ADJUDICATION)
    entries = adj["edges"]

    action_counts = Counter(e["action"] for e in entries)
    print(f"\nDecisions loaded: {dict(action_counts)}")

    # Group by module
    actions_by_module = defaultdict(list)
    for entry in entries:
        actions_by_module[entry["module"]].append(entry)

    # Tracking
    deleted_edges = []
    accept_edges_for_verify = []  # (edge_ref, new_type, new_id, candidate_info)
    warnings = []
    actions_applied = {"accept": 0, "archive": 0, "delete": 0, "keep": 0}

    # Process each module
    mfiles = module_files()
    print(f"\nProcessing {len(mfiles)} module files...")

    for mfile in mfiles:
        module_name = os.path.basename(mfile)
        if module_name not in actions_by_module:
            continue

        edges = load_json(mfile)
        module_actions = actions_by_module[module_name]
        modified = False
        edges_to_delete = []

        for act_entry in module_actions:
            action = act_entry["action"]
            src = act_entry["source_node"]
            tgt = act_entry["target_node"]
            current_id = act_entry["current_id"]

            # Find matching edge
            match_idx = None
            for idx, edge in enumerate(edges):
                if edge["source_node"] == src and edge["target_node"] == tgt:
                    # Confirm current citation matches
                    cit = edge.get("evidence_citation", "")
                    if current_id in cit:
                        match_idx = idx
                        break

            if match_idx is None:
                # Try looser match (just source+target)
                for idx, edge in enumerate(edges):
                    if edge["source_node"] == src and edge["target_node"] == tgt:
                        match_idx = idx
                        break

            if match_idx is None:
                warnings.append(f"No match found: {module_name} :: {src} -> {tgt}")
                print(f"  WARNING: No match for {src} -> {tgt} in {module_name}")
                continue

            edge = edges[match_idx]
            old_type = edge.get("evidence_type", "")
            old_id = current_id
            old_citation = edge.get("evidence_citation", "")

            if action.startswith("ACCEPT"):
                rank = int(action.split()[1])
                candidate = next((c for c in act_entry["candidates"] if c["rank"] == rank), None)
                if not candidate:
                    warnings.append(f"Candidate rank {rank} not found: {module_name} :: {src} -> {tgt}")
                    continue

                new_type = candidate["type"]
                new_id = candidate["id"]

                # Update citation fields
                if new_type == "PMID":
                    edge["evidence_citation"] = f"PMID: {new_id}"
                    edge["evidence_type"] = "PMID"
                    edge["evidence_locator"] = f"https://pubmed.ncbi.nlm.nih.gov/{new_id}/"
                elif new_type == "DOI":
                    edge["evidence_citation"] = f"DOI: {new_id}"
                    edge["evidence_type"] = "DOI"
                    edge["evidence_locator"] = f"https://doi.org/{new_id}"

                # Update notes
                clean_notes = strip_verification_stamps(edge.get("notes", ""))
                stamp = f"[Phase2 replaced {old_type}: {old_id} -> {new_type}: {new_id} on 2026-03-17]"
                edge["notes"] = f"{stamp} {clean_notes}"

                # Restore confidence
                edge["confidence"] = "high"

                modified = True
                actions_applied["accept"] += 1

                accept_edges_for_verify.append({
                    "module": module_name,
                    "source_node": src,
                    "target_node": tgt,
                    "new_type": new_type,
                    "new_id": new_id,
                    "candidate": candidate,
                    "edge_ref_idx": match_idx
                })

            elif action == "ARCHIVE":
                clean_notes = strip_verification_stamps(edge.get("notes", ""))
                archive_cit = build_archive_citation(edge, clean_notes)
                archive_loc = build_archive_locator(edge, clean_notes)

                edge["evidence_citation"] = archive_cit
                edge["evidence_type"] = "institutional_archive"
                edge["evidence_locator"] = archive_loc

                stamp = f"[Phase2 downgraded from {old_type}: {old_id} to institutional_archive on 2026-03-17 — no PubMed source found]"
                edge["notes"] = f"{stamp} {clean_notes}"
                edge["confidence"] = "moderate"

                modified = True
                actions_applied["archive"] += 1

            elif action == "DELETE":
                edges_to_delete.append(match_idx)
                deleted_edges.append({
                    "module": module_name,
                    "source_node": src,
                    "target_node": tgt,
                    "edge_type": edge.get("edge_type", ""),
                    "temporal_range": edge.get("temporal_range", ""),
                    "old_citation": old_citation,
                    "reason": "Manual review — relationship unverifiable; no PubMed source found"
                })
                actions_applied["delete"] += 1
                modified = True

            elif action == "KEEP":
                clean_notes = strip_verification_stamps(edge.get("notes", ""))
                stamp = "[Phase2 reviewed — citation retained on 2026-03-17]"
                edge["notes"] = f"{stamp} {clean_notes}"

                # Restore confidence if it was downgraded
                if edge.get("confidence") == "low":
                    edge["confidence"] = "high"

                modified = True
                actions_applied["keep"] += 1

        # Apply deletions (reverse order to preserve indices)
        for idx in sorted(edges_to_delete, reverse=True):
            edges.pop(idx)

        if modified:
            # Preserve key ordering
            edges = [ordered_edge(e) for e in edges]
            save_json(mfile, edges)
            print(f"  Updated: {module_name} ({len(module_actions)} actions, {len(edges_to_delete)} deleted)")

    print(f"\nActions applied: {dict(actions_applied)}")
    print(f"Warnings: {len(warnings)}")
    for w in warnings:
        print(f"  {w}")

    # Save deleted edges
    save_json(DELETED_OUT, deleted_edges)
    print(f"\nDeleted edges saved to: {DELETED_OUT}")

    # ---------- Step 7: Re-verify newly inserted PMIDs/DOIs ----------
    print("\n--- Re-verification of newly inserted citations ---\n")

    # Separate PMIDs and DOIs
    new_pmids = [(a["new_id"], a) for a in accept_edges_for_verify if a["new_type"] == "PMID"]
    new_dois = [(a["new_id"], a) for a in accept_edges_for_verify if a["new_type"] == "DOI"]

    print(f"New PMIDs to verify: {len(new_pmids)}")
    print(f"New DOIs to verify: {len(new_dois)}")

    # Batch fetch PMIDs
    unique_pmids = list(set(p[0] for p in new_pmids))
    print(f"Unique PMIDs: {len(unique_pmids)}")

    pmid_corpus = {}
    batch_size = 50
    for i in range(0, len(unique_pmids), batch_size):
        batch = unique_pmids[i:i+batch_size]
        print(f"  Fetching PMID batch {i//batch_size + 1}...")
        result = efetch_batch(batch)
        pmid_corpus.update(result)
        if i + batch_size < len(unique_pmids):
            time.sleep(NCBI_DELAY)

    # Fetch DOIs
    doi_corpus = {}
    unique_dois = list(set(d[0] for d in new_dois))
    for doi in unique_dois:
        print(f"  Fetching DOI: {doi}")
        result = fetch_crossref(doi)
        if result:
            doi_corpus[doi] = result
        time.sleep(CROSSREF_DELAY)

    # Score and stamp each ACCEPT edge
    verify_passed = 0
    verify_failed = 0
    verify_failures = []

    # Need to reload modified modules to stamp verification results
    for mfile in mfiles:
        module_name = os.path.basename(mfile)
        edges = load_json(mfile)
        module_modified = False

        for accept_info in accept_edges_for_verify:
            if accept_info["module"] != module_name:
                continue

            src = accept_info["source_node"]
            tgt = accept_info["target_node"]
            new_type = accept_info["new_type"]
            new_id = accept_info["new_id"]

            # Find the edge
            edge = None
            for e in edges:
                if e["source_node"] == src and e["target_node"] == tgt:
                    edge = e
                    break
            if not edge:
                continue

            # Get article
            article = None
            if new_type == "PMID":
                article = pmid_corpus.get(new_id)
            elif new_type == "DOI":
                article = doi_corpus.get(new_id)

            if not article:
                # Existence check failed
                verify_failed += 1
                verify_failures.append({
                    "module": module_name,
                    "source_node": src,
                    "target_node": tgt,
                    "new_type": new_type,
                    "new_id": new_id,
                    "error": "Article not found via efetch/CrossRef"
                })
                # Update stamp
                notes = edge.get("notes", "")
                edge["notes"] = notes.replace("[Phase2 replaced", "[RE-VERIFY FAILED 2026-03-17 — candidate did not resolve] [Phase2 replaced")
                edge["confidence"] = "low"
                module_modified = True
                continue

            # Content match score
            edge_tokens = build_edge_tokens(edge)
            score = score_match(edge_tokens, article)

            journal = article.get("journal", "")
            year = article.get("year", "")

            if score >= 0.20:
                verify_passed += 1
                stamp = f"[Verified 2026-03-17 | {journal} {year} | content_match]"
            elif score >= 0.05:
                verify_passed += 1
                stamp = f"[Verified 2026-03-17 | {journal} {year} | weak_match]"
            else:
                verify_failed += 1
                stamp = f"[Verified 2026-03-17 | {journal} {year} | MISMATCH: re-verify]"
                edge["confidence"] = "low"
                verify_failures.append({
                    "module": module_name,
                    "source_node": src,
                    "target_node": tgt,
                    "new_type": new_type,
                    "new_id": new_id,
                    "score": score,
                    "article_title": article.get("title", ""),
                    "error": f"Content mismatch (score={score:.3f})"
                })

            # Insert verification stamp after Phase2 stamp
            notes = edge.get("notes", "")
            # Insert after the closing ] of Phase2 stamp
            notes = re.sub(r'(\[Phase2 replaced[^\]]*\])', r'\1 ' + stamp, notes, count=1)
            edge["notes"] = notes
            module_modified = True

        if module_modified:
            edges = [ordered_edge(e) for e in edges]
            save_json(mfile, edges)

    print(f"\nRe-verification results:")
    print(f"  Passed: {verify_passed}")
    print(f"  Failed: {verify_failed}")
    if verify_failures:
        for f in verify_failures:
            print(f"  FAIL: {f['module']} :: {f['source_node']} -> {f['target_node']} — {f['error']}")

    # ---------- Step 8: Regenerate canonical graph ----------
    print("\nRegenerating canonical graph...")
    all_edges = []
    for mfile in mfiles:
        module_name = os.path.basename(mfile)
        edges = load_json(mfile)
        for edge in edges:
            edge_copy = dict(edge)
            edge_copy["module"] = module_name
            all_edges.append(edge_copy)
    all_edges.sort(key=lambda e: (e.get("start_year", 9999), e.get("source_node", "")))
    save_json(CANONICAL, all_edges)
    print(f"  Saved: {len(all_edges)} edges")

    # ---------- Step 10: Produce Phase 2 report ----------
    print("\nWriting Phase 2 report...")

    # Count citation types across all modules
    type_counts = Counter()
    for mfile in mfiles:
        for e in load_json(mfile):
            type_counts[e.get("evidence_type", "unknown")] += 1

    report = {
        "run_date": "2026-03-17",
        "actions_applied": {
            "accept": actions_applied["accept"],
            "archive": actions_applied["archive"],
            "delete": actions_applied["delete"],
            "keep": actions_applied["keep"]
        },
        "edges_before": 385,
        "edges_after": len(all_edges),
        "re_verification": {
            "pmids_checked": len(unique_pmids),
            "dois_checked": len(unique_dois),
            "passed": verify_passed,
            "failed": verify_failed,
            "failures": verify_failures
        },
        "deleted_edges": deleted_edges,
        "citation_type_summary": dict(type_counts),
        "warnings": warnings
    }
    save_json(REPORT_OUT, report)
    print(f"  Saved: {REPORT_OUT}")

    # Summary
    print("\n" + "=" * 60)
    print("Phase 2 Summary")
    print("=" * 60)
    print(f"  Edges before:    {report['edges_before']}")
    print(f"  Edges after:     {report['edges_after']}")
    print(f"  ACCEPT applied:  {actions_applied['accept']}")
    print(f"  ARCHIVE applied: {actions_applied['archive']}")
    print(f"  DELETE applied:  {actions_applied['delete']}")
    print(f"  KEEP applied:    {actions_applied['keep']}")
    print(f"  Re-verify pass:  {verify_passed}")
    print(f"  Re-verify fail:  {verify_failed}")
    print(f"\n  Citation types:")
    for k, v in type_counts.most_common():
        print(f"    {k}: {v}")

if __name__ == "__main__":
    main()
