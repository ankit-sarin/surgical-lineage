#!/usr/bin/env python3
"""
Phase 1.5: Content-Match Validation of Verified Citations

For each verified PMID/DOI edge, checks whether the resolved article
actually relates to the edge it is cited on.
"""

import json
import glob
import os
import re
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from collections import defaultdict

BASE = "/Users/asarin/Library/CloudStorage/Dropbox/PROJECTS/@ STRIVE/2026 Surgical lineage"
REPORT_PATH = os.path.join(BASE, "verification_report_phase1.json")
REPORT_OUT = os.path.join(BASE, "verification_report_phase1_5.json")
CANONICAL = os.path.join(BASE, "surgical_lineage_graph_canonical.json")

# Rate limiting
NCBI_DELAY = 0.35  # ~3 req/sec
CROSSREF_DELAY = 0.5

# ---------- helpers ----------

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')

def module_files():
    """Return sorted list of module files (01-14)."""
    pattern = os.path.join(BASE, "[0-1][0-9]_*.json")
    files = sorted(glob.glob(pattern))
    # Exclude 00_schema.json
    return [f for f in files if not os.path.basename(f).startswith("00_")]

# ---------- Step 1: Fetch abstracts from PubMed ----------

def fetch_pubmed_batch(pmids):
    """Fetch PubMed articles via efetch for a batch of PMIDs. Returns dict pmid -> {title, abstract, journal, year, authors}."""
    results = {}
    if not pmids:
        return results

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "xml",
        "retmode": "xml"
    }
    full_url = f"{url}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(full_url, headers={"User-Agent": "SurgicalLineageValidator/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_data = resp.read().decode('utf-8')
    except Exception as e:
        print(f"  ERROR fetching batch: {e}")
        return results

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"  ERROR parsing XML: {e}")
        return results

    for article in root.findall('.//PubmedArticle'):
        # Get PMID
        pmid_el = article.find('.//PMID')
        if pmid_el is None:
            continue
        pmid = pmid_el.text

        # Get title
        title_el = article.find('.//ArticleTitle')
        title = title_el.text if title_el is not None and title_el.text else ""
        # Handle mixed content (title with sub-elements)
        if title_el is not None:
            title = ''.join(title_el.itertext())

        # Get abstract
        abstract_parts = []
        for abs_el in article.findall('.//AbstractText'):
            text = ''.join(abs_el.itertext())
            if text:
                abstract_parts.append(text)
        abstract = ' '.join(abstract_parts)

        # Get journal
        journal_el = article.find('.//MedlineTA')
        journal = journal_el.text if journal_el is not None else ""

        # Get year
        year = ""
        year_el = article.find('.//PubDate/Year')
        if year_el is not None:
            year = year_el.text
        else:
            medline_year = article.find('.//PubDate/MedlineDate')
            if medline_year is not None and medline_year.text:
                m = re.search(r'(\d{4})', medline_year.text)
                if m:
                    year = m.group(1)

        # Get authors
        authors = []
        for author in article.findall('.//Author'):
            last = author.find('LastName')
            if last is not None and last.text:
                authors.append(last.text)

        results[pmid] = {
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "year": year,
            "authors": authors
        }

    return results

def fetch_all_pubmed_abstracts(pmid_list):
    """Fetch abstracts for all PMIDs in batches of 50."""
    corpus = {}
    batch_size = 50
    total = len(pmid_list)

    for i in range(0, total, batch_size):
        batch = pmid_list[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size
        print(f"  Fetching PubMed batch {batch_num}/{total_batches} ({len(batch)} PMIDs)...")

        result = fetch_pubmed_batch(batch)
        corpus.update(result)

        if i + batch_size < total:
            time.sleep(NCBI_DELAY)

    return corpus

# ---------- Step 1b: Fetch DOI metadata from CrossRef ----------

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
        print(f"  ERROR fetching DOI {doi}: {e}")
        return None

    msg = data.get("message", {})

    title_list = msg.get("title", [])
    title = title_list[0] if title_list else ""

    # Abstract (CrossRef sometimes has it)
    abstract = msg.get("abstract", "")
    # Strip HTML tags from abstract
    abstract = re.sub(r'<[^>]+>', '', abstract)

    authors = []
    for a in msg.get("author", []):
        family = a.get("family", "")
        if family:
            authors.append(family)

    container = msg.get("container-title", [])
    journal = container[0] if container else ""

    year = ""
    issued = msg.get("issued", {})
    parts = issued.get("date-parts", [[]])
    if parts and parts[0]:
        year = str(parts[0][0])

    return {
        "title": title,
        "abstract": abstract,
        "journal": journal,
        "year": year,
        "authors": authors
    }

def fetch_all_crossref(doi_list):
    """Fetch metadata for all DOIs."""
    corpus = {}
    for i, doi in enumerate(doi_list):
        print(f"  Fetching CrossRef {i+1}/{len(doi_list)}: {doi}")
        result = fetch_crossref(doi)
        if result:
            corpus[doi] = result
        if i < len(doi_list) - 1:
            time.sleep(CROSSREF_DELAY)
    return corpus

# ---------- Step 2: Build edge token sets ----------

def build_edge_tokens(edge):
    """Extract match tokens from edge metadata."""
    tokens = set()

    # Person/institution names from source and target
    for field in ['source_node', 'target_node']:
        name = edge.get(field, '')
        tokens.add(name.lower())
        for part in name.split():
            clean = part.lower().rstrip('.')
            if len(clean) > 2:
                tokens.add(clean)

    # Key terms from notes (first 200 chars, skip the verification stamp)
    notes = edge.get('notes', '')
    # Strip the [Verified ...] stamp before extracting tokens
    notes_clean = re.sub(r'\[Verified[^\]]*\]\s*', '', notes)
    notes_excerpt = notes_clean[:200]
    for word in notes_excerpt.split():
        clean = word.lower().strip('.,;:()[]"\'-')
        if len(clean) > 4:
            tokens.add(clean)

    return tokens

# ---------- Step 3: Score match ----------

def score_match(edge_tokens, article):
    """Compute content-match score between edge tokens and article metadata."""
    searchable = ' '.join([
        article.get('title', ''),
        article.get('abstract', ''),
        ' '.join(article.get('authors', []))
    ]).lower()

    matches = 0
    checked = 0
    matched_tokens = []
    missed_tokens = []

    for token in edge_tokens:
        if len(token) > 2:
            checked += 1
            if token in searchable:
                matches += 1
                matched_tokens.append(token)
            else:
                missed_tokens.append(token)

    score = matches / max(checked, 1)
    return score, matched_tokens, missed_tokens

# ---------- Step 4: Process edges ----------

def extract_pmid(citation):
    """Extract PMID number from evidence_citation field."""
    m = re.search(r'PMID:\s*(\d+)', citation)
    return m.group(1) if m else None

def extract_doi(citation):
    """Extract DOI from evidence_citation field."""
    m = re.search(r'DOI:\s*(10\.\S+)', citation)
    return m.group(1) if m else None

def has_phase15_stamp(notes):
    """Check if notes already have a Phase 1.5 stamp."""
    return any(tag in notes for tag in ['content_match', 'weak_match', 'MISMATCH'])

def has_phase1_stamp(notes):
    """Check if notes have a Phase 1 verification stamp."""
    return '[Verified 2026-03-17' in notes

def has_verify_failed(notes):
    """Check if notes have VERIFY_FAILED stamp."""
    return '[VERIFY_FAILED' in notes

def update_stamp(notes, label):
    """Append the Phase 1.5 label inside the existing Phase 1 stamp bracket."""
    # Pattern: [Verified 2026-03-17 | Journal Year]
    # -> [Verified 2026-03-17 | Journal Year | label]
    pattern = r'(\[Verified 2026-03-17 \| [^\]]+)\]'
    replacement = r'\1 | ' + label + ']'
    updated = re.sub(pattern, replacement, notes, count=1)
    return updated

# ---------- Main ----------

def main():
    print("=" * 60)
    print("Phase 1.5: Content-Match Validation")
    print("=" * 60)

    # Load Phase 1 report
    print("\nLoading Phase 1 report...")
    report = load_json(REPORT_PATH)
    pmid_map = report.get("verified_pmid_map", {})
    doi_map = report.get("verified_doi_map", {})

    # Collect verified PMIDs and DOIs
    verified_pmids = [p for p, info in pmid_map.items() if info.get("status") == "verified"]
    verified_dois = [d for d, info in doi_map.items() if info.get("status") == "verified"]

    print(f"  Verified PMIDs: {len(verified_pmids)}")
    print(f"  Verified DOIs: {len(verified_dois)}")

    # Step 1: Fetch abstracts
    print("\nStep 1: Fetching PubMed abstracts...")
    pmid_corpus = fetch_all_pubmed_abstracts(verified_pmids)
    print(f"  Fetched {len(pmid_corpus)} PubMed records")

    # Count how many have abstracts
    with_abstract = sum(1 for v in pmid_corpus.values() if v.get('abstract'))
    print(f"  Records with abstracts: {with_abstract}")
    print(f"  Records without abstracts (title+authors only): {len(pmid_corpus) - with_abstract}")

    print("\nStep 1b: Fetching CrossRef metadata...")
    doi_corpus = fetch_all_crossref(verified_dois)
    print(f"  Fetched {len(doi_corpus)} CrossRef records")

    # Step 2-4: Process all module files
    print("\nStep 2-4: Processing module files...")

    mfiles = module_files()
    print(f"  Found {len(mfiles)} module files")

    # Tracking
    stats = {
        "edges_checked": 0,
        "content_match": 0,
        "weak_match": 0,
        "mismatch": 0,
        "skipped_failed": 0,
        "skipped_already_stamped": 0,
        "skipped_no_corpus": 0
    }
    weak_matches = []
    mismatches = []
    all_scores = []  # For debugging

    for mfile in mfiles:
        module_name = os.path.basename(mfile)
        edges = load_json(mfile)
        modified = False

        for edge in edges:
            ev_type = edge.get("evidence_type", "")
            notes = edge.get("notes", "")

            # Skip non-PMID/DOI edges
            if ev_type not in ("PMID", "DOI"):
                continue

            # Skip VERIFY_FAILED
            if has_verify_failed(notes):
                stats["skipped_failed"] += 1
                continue

            # Skip if no Phase 1 stamp
            if not has_phase1_stamp(notes):
                continue

            # Idempotency: skip if already has Phase 1.5 stamp
            if has_phase15_stamp(notes):
                stats["skipped_already_stamped"] += 1
                continue

            # Get the article from corpus
            citation = edge.get("evidence_citation", "")
            article = None
            id_val = None
            id_type = None

            if ev_type == "PMID":
                pmid = extract_pmid(citation)
                if pmid and pmid in pmid_corpus:
                    article = pmid_corpus[pmid]
                    id_val = pmid
                    id_type = "pmid"
                elif pmid:
                    stats["skipped_no_corpus"] += 1
                    continue
                else:
                    continue
            elif ev_type == "DOI":
                doi = extract_doi(citation)
                if doi and doi in doi_corpus:
                    article = doi_corpus[doi]
                    id_val = doi
                    id_type = "doi"
                elif doi:
                    stats["skipped_no_corpus"] += 1
                    continue
                else:
                    continue

            # Build tokens and score
            edge_tokens = build_edge_tokens(edge)
            score, matched, missed = score_match(edge_tokens, article)

            stats["edges_checked"] += 1

            edge_label = f"{edge.get('source_node', '?')} -> {edge.get('target_node', '?')}"

            all_scores.append({
                "id": id_val,
                "type": id_type,
                "module": module_name,
                "edge": edge_label,
                "score": round(score, 3),
                "matched": matched[:5],  # Top 5
                "article_title": article.get("title", "")[:80]
            })

            if score >= 0.20:
                # CONTENT_MATCH
                stats["content_match"] += 1
                edge["notes"] = update_stamp(notes, "content_match")
                modified = True

            elif score >= 0.05:
                # WEAK_MATCH
                stats["weak_match"] += 1
                matched_str = ', '.join(f'"{t}"' for t in matched[:4])
                missed_names = [t for t in missed if len(t) > 3][:3]
                missed_str = ', '.join(missed_names)
                label = f'weak_match: matched {matched_str}; missed {missed_str}'
                edge["notes"] = update_stamp(notes, label)
                modified = True

                weak_matches.append({
                    id_type: id_val,
                    "module": module_name,
                    "edge": edge_label,
                    "score": round(score, 3),
                    "matched_tokens": matched,
                    "missed_tokens": missed_names,
                    "article_title": article.get("title", "")
                })

            else:
                # MISMATCH
                stats["mismatch"] += 1
                label = f'MISMATCH: {len(matched)} of {len(matched)+len(missed)} edge tokens found in article'
                edge["notes"] = update_stamp(notes, label)
                # Downgrade confidence
                old_conf = edge.get("confidence", "medium")
                edge["confidence"] = "low"
                modified = True

                mismatches.append({
                    id_type: id_val,
                    "module": module_name,
                    "edge": edge_label,
                    "score": round(score, 3),
                    "article_title": article.get("title", ""),
                    "matched_tokens": matched,
                    "prior_confidence": old_conf,
                    "recommendation": "Manual review -- PMID/DOI may be incorrect"
                })

        if modified:
            save_json(mfile, edges)
            print(f"  Updated: {module_name}")

    # Print score distribution for debugging
    print("\n--- Score Distribution ---")
    if all_scores:
        sorted_scores = sorted(all_scores, key=lambda x: x["score"])
        print(f"  Lowest 10 scores:")
        for s in sorted_scores[:10]:
            print(f"    {s['score']:.3f}  {s['id']}  {s['module']}  {s['edge'][:50]}")
            print(f"           Article: {s['article_title']}")
        print(f"  Highest 5 scores:")
        for s in sorted_scores[-5:]:
            print(f"    {s['score']:.3f}  {s['id']}  {s['module']}  {s['edge'][:50]}")

    # Step 6: Write report
    print("\nStep 6: Writing Phase 1.5 report...")
    phase15_report = {
        "run_date": "2026-03-17",
        "edges_checked": stats["edges_checked"],
        "content_match": stats["content_match"],
        "weak_match": stats["weak_match"],
        "mismatch": stats["mismatch"],
        "skipped_failed": stats["skipped_failed"],
        "skipped_already_stamped": stats["skipped_already_stamped"],
        "skipped_no_corpus": stats["skipped_no_corpus"],
        "weak_matches": weak_matches,
        "mismatches": mismatches
    }
    save_json(REPORT_OUT, phase15_report)
    print(f"  Saved: {REPORT_OUT}")

    # Step 5: Regenerate canonical graph
    print("\nStep 5: Regenerating canonical graph...")
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
    print(f"  Saved: {CANONICAL} ({len(all_edges)} edges)")

    # Summary
    print("\n" + "=" * 60)
    print("Phase 1.5 Summary")
    print("=" * 60)
    print(f"  Edges checked:          {stats['edges_checked']}")
    print(f"  Content matches:        {stats['content_match']}")
    print(f"  Weak matches:           {stats['weak_match']}")
    print(f"  Mismatches:             {stats['mismatch']}")
    print(f"  Skipped (VERIFY_FAILED):{stats['skipped_failed']}")
    print(f"  Skipped (already done): {stats['skipped_already_stamped']}")
    print(f"  Skipped (no corpus):    {stats['skipped_no_corpus']}")

    if mismatches:
        print(f"\n  MISMATCHES requiring manual review:")
        for mm in mismatches:
            id_key = "pmid" if "pmid" in mm else "doi"
            print(f"    {mm[id_key]} | {mm['module']} | {mm['edge']}")
            print(f"      Article: {mm['article_title'][:80]}")
            print(f"      Score: {mm['score']}")

    if weak_matches:
        print(f"\n  WEAK MATCHES for review:")
        for wm in weak_matches:
            id_key = "pmid" if "pmid" in wm else "doi"
            print(f"    {wm[id_key]} | {wm['module']} | {wm['edge']}")
            print(f"      Score: {wm['score']} | Matched: {wm['matched_tokens'][:3]}")

if __name__ == "__main__":
    main()
