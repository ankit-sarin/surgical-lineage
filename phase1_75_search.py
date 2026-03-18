#!/usr/bin/env python3
"""
Phase 1.75: Search for Replacement Citations

For every edge flagged as MISMATCH or weak_match in Phase 1.5, search PubMed
for candidate replacement PMIDs. Produces a review document and JSON companion.
READ-ONLY with respect to module files.
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
REPORT_PATH = os.path.join(BASE, "verification_report_phase1_5.json")
MD_OUT = os.path.join(BASE, "CITATION_REPAIR_CANDIDATES.md")
JSON_OUT = os.path.join(BASE, "citation_repair_candidates.json")

NCBI_DELAY = 0.35
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
    pattern = os.path.join(BASE, "[0-1][0-9]_*.json")
    files = sorted(glob.glob(pattern))
    return [f for f in files if not os.path.basename(f).startswith("00_")]

# ---------- Load all edges for context ----------

def load_all_edges():
    """Load all edges from all modules, keyed by (module, source->target)."""
    edges_map = {}
    for mfile in module_files():
        module_name = os.path.basename(mfile)
        edges = load_json(mfile)
        for edge in edges:
            key = f"{module_name}::{edge['source_node']}->{edge['target_node']}"
            edges_map[key] = edge
    return edges_map

# ---------- PubMed esearch ----------

def esearch(query, retmax=5):
    """Search PubMed and return list of PMIDs."""
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "retmax": str(retmax),
        "retmode": "json",
        "term": query
    }
    full_url = f"{url}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(full_url, headers={"User-Agent": "SurgicalLineageValidator/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        result = data.get("esearchresult", {})
        return result.get("idlist", [])
    except Exception as e:
        print(f"    esearch error: {e}")
        return []

# ---------- PubMed efetch ----------

def efetch_batch(pmids):
    """Fetch article metadata for a batch of PMIDs."""
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
        print(f"    efetch error: {e}")
        return results

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
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
            medline_year = article.find('.//PubDate/MedlineDate')
            if medline_year is not None and medline_year.text:
                m = re.search(r'(\d{4})', medline_year.text)
                if m:
                    year = m.group(1)

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

# ---------- CrossRef search ----------

def crossref_search(query_str, rows=5):
    """Search CrossRef and return list of {doi, title, journal, year, authors, abstract}."""
    url = f"https://api.crossref.org/works?query={urllib.parse.quote(query_str)}&rows={rows}"

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "SurgicalLineageValidator/1.0 (mailto:research@digitalsurgeon.dev)"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"    CrossRef search error: {e}")
        return []

    results = []
    for item in data.get("message", {}).get("items", []):
        doi = item.get("DOI", "")
        title_list = item.get("title", [])
        title = title_list[0] if title_list else ""
        abstract = re.sub(r'<[^>]+>', '', item.get("abstract", ""))
        container = item.get("container-title", [])
        journal = container[0] if container else ""
        year = ""
        issued = item.get("issued", {})
        parts = issued.get("date-parts", [[]])
        if parts and parts[0]:
            year = str(parts[0][0])
        authors = [a.get("family", "") for a in item.get("author", []) if a.get("family")]

        results.append({
            "doi": doi,
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "year": year,
            "authors": authors
        })

    return results

# ---------- Scoring ----------

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
    notes_clean = re.sub(r'\[Verified[^\]]*\]\s*', '', notes)
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
    matched_tokens = []

    for token in edge_tokens:
        if len(token) > 2:
            checked += 1
            if token in searchable:
                matches += 1
                matched_tokens.append(token)

    score = matches / max(checked, 1)
    return score, matched_tokens

# ---------- Query builders ----------

def extract_surname(full_name):
    """Extract the primary surname from a full name."""
    parts = full_name.split()
    # Handle suffixes like Jr., III, etc.
    suffixes = {'jr.', 'jr', 'sr.', 'sr', 'ii', 'iii', 'iv', 'md', 'phd'}
    clean_parts = [p for p in parts if p.lower().rstrip('.') not in suffixes]
    if clean_parts:
        return clean_parts[-1].rstrip('.')
    return parts[-1].rstrip('.') if parts else ""

def extract_institution_keywords(name):
    """Extract meaningful keywords from institution name."""
    stopwords = {'the', 'of', 'for', 'and', 'in', 'at', 'to', 'a', 'an', 'department', 'program', 'section'}
    words = [w for w in name.split() if w.lower() not in stopwords and len(w) > 2]
    return words[:3]  # Top 3 meaningful words

def build_queries(edge):
    """Build up to 3 tiers of PubMed queries for an edge."""
    queries = []
    source = edge.get('source_node', '')
    target = edge.get('target_node', '')
    source_type = edge.get('source_node_type', '')
    target_type = edge.get('target_node_type', '')
    edge_type = edge.get('edge_type', '')

    source_surname = extract_surname(source)
    target_surname = extract_surname(target)

    # Determine person and institution
    person1 = source_surname if source_type == 'person' else ""
    person2 = target_surname if target_type == 'person' else ""
    institution = ""
    if source_type == 'institution':
        institution = source
    elif target_type == 'institution':
        institution = target

    inst_keywords = extract_institution_keywords(institution) if institution else []

    # Tier 1: Specific relationship query
    if edge_type in ('direct_training', 'observational_study'):
        if person1 and person2:
            q = f'"{person2}"[Title/Abstract] AND ("surgical training" OR "surgical residency" OR "biography" OR "history" OR "mentor") AND "{person1}"[Title/Abstract]'
            queries.append(q)
        elif person1 and inst_keywords:
            inst_part = " OR ".join(f'"{w}"[Title/Abstract]' for w in inst_keywords[:2])
            q = f'"{person1}"[Title/Abstract] AND ("surgical training" OR "residency" OR "history") AND ({inst_part})'
            queries.append(q)
        elif person2 and inst_keywords:
            inst_part = " OR ".join(f'"{w}"[Title/Abstract]' for w in inst_keywords[:2])
            q = f'"{person2}"[Title/Abstract] AND ("surgical training" OR "residency" OR "history") AND ({inst_part})'
            queries.append(q)

    elif edge_type in ('institutional_founder', 'institutional_succession'):
        person = person1 or person2
        if person and inst_keywords:
            inst_part = " AND ".join(f'"{w}"[Title/Abstract]' for w in inst_keywords[:2])
            q = f'"{person}"[Title/Abstract] AND {inst_part} AND ("chairman" OR "chair" OR "department" OR "history" OR "founded")'
            queries.append(q)
        elif inst_keywords:
            inst_part = " AND ".join(f'"{w}"[Title/Abstract]' for w in inst_keywords[:2])
            q = f'{inst_part} AND ("history" OR "founded" OR "department") AND surgery'
            queries.append(q)

    elif edge_type in ('governance_leadership', 'society_founder'):
        person = person1 or person2
        society = institution
        if person and society:
            soc_keywords = extract_institution_keywords(society)
            soc_part = " AND ".join(f'"{w}"[Title/Abstract]' for w in soc_keywords[:2])
            q = f'"{person}"[Title/Abstract] AND ({soc_part} OR "president" OR "leadership") AND ("surgery" OR "surgical")'
            queries.append(q)
        elif person:
            q = f'"{person}"[Title/Abstract] AND ("president" OR "leadership") AND ("surgery" OR "surgical")'
            queries.append(q)

    elif edge_type == 'programmatic_accreditation':
        if inst_keywords:
            inst_part = " AND ".join(f'"{w}"[Title/Abstract]' for w in inst_keywords[:2])
            q = f'{inst_part} AND ("accreditation" OR "board" OR "certification") AND surgery'
            queries.append(q)

    # If no tier 1 was generated, use a generic first attempt
    if not queries:
        parts = []
        if person1:
            parts.append(f'"{person1}"[Title/Abstract]')
        if person2:
            parts.append(f'"{person2}"[Title/Abstract]')
        if inst_keywords:
            parts.append(f'"{inst_keywords[0]}"[Title/Abstract]')
        if parts:
            queries.append(' AND '.join(parts) + ' AND surgery')

    # Tier 2: Broader — both names + surgery
    names = []
    if person1:
        names.append(f'"{person1}"[Title/Abstract]')
    if person2:
        names.append(f'"{person2}"[Title/Abstract]')
    if len(names) == 2:
        queries.append(f'{names[0]} AND {names[1]} AND surgery')
    elif len(names) == 1 and inst_keywords:
        queries.append(f'{names[0]} AND "{inst_keywords[0]}"[Title/Abstract] AND surgery')

    # Tier 3: Obituary/tribute/biography search
    persons = [p for p in [person1, person2] if p]
    for p in persons[:1]:  # Only first person
        queries.append(f'"{p}"[Title] AND (obituary OR "in memoriam" OR tribute OR biography OR "history of") AND (surgery OR surgical)')

    # Tier 3b: Name in major surgery journals
    for p in persons[:1]:
        queries.append(f'"{p}"[Title] AND (Ann Surg[Journal] OR Surgery[Journal] OR "J Am Coll Surg"[Journal] OR "Am J Surg"[Journal])')

    # Deduplicate while preserving order
    seen = set()
    unique_queries = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            unique_queries.append(q)

    return unique_queries[:4]  # Max 4 tiers

# ---------- Main search logic ----------

def search_for_edge(edge, all_candidate_pmids_seen):
    """Search PubMed for candidate replacements for a single edge.
    Returns list of scored candidates."""
    queries = build_queries(edge)
    all_pmids = []
    queries_tried = []

    current_pmid = None
    citation = edge.get('evidence_citation', '')
    m = re.search(r'PMID:\s*(\d+)', citation)
    if m:
        current_pmid = m.group(1)

    for qi, query in enumerate(queries):
        pmids = esearch(query, retmax=5)
        queries_tried.append(query)
        # Exclude the current bad PMID
        pmids = [p for p in pmids if p != current_pmid]
        all_pmids.extend(pmids)

        time.sleep(NCBI_DELAY)

        if pmids:
            break  # Found results, stop searching tiers

    # Deduplicate
    seen = set()
    unique_pmids = []
    for p in all_pmids:
        if p not in seen:
            seen.add(p)
            unique_pmids.append(p)

    if not unique_pmids:
        return [], queries_tried

    # Fetch metadata
    time.sleep(NCBI_DELAY)
    articles = efetch_batch(unique_pmids)

    # Score each
    edge_tokens = build_edge_tokens(edge)
    scored = []
    for pmid, article in articles.items():
        score, matched = score_match(edge_tokens, article)
        if score >= 0.20:
            scored.append({
                "type": "PMID",
                "id": pmid,
                "title": article.get("title", ""),
                "journal": article.get("journal", ""),
                "year": article.get("year", ""),
                "score": round(score, 3),
                "matched_tokens": matched
            })

    # Sort by score descending, take top 3
    scored.sort(key=lambda x: -x["score"])
    return scored[:3], queries_tried

def crossref_fallback(edge):
    """Search CrossRef for DOI candidates when PubMed fails."""
    source = edge.get('source_node', '')
    target = edge.get('target_node', '')
    source_type = edge.get('source_node_type', '')
    target_type = edge.get('target_node_type', '')

    query_parts = []
    if source_type == 'person':
        query_parts.append(extract_surname(source))
    if target_type == 'person':
        query_parts.append(extract_surname(target))
    if source_type == 'institution':
        query_parts.extend(extract_institution_keywords(source)[:2])
    if target_type == 'institution':
        query_parts.extend(extract_institution_keywords(target)[:2])
    query_parts.append("surgery history")

    query_str = ' '.join(query_parts)
    results = crossref_search(query_str, rows=5)

    edge_tokens = build_edge_tokens(edge)
    scored = []
    for r in results:
        score, matched = score_match(edge_tokens, r)
        if score >= 0.20:
            scored.append({
                "type": "DOI",
                "id": r["doi"],
                "title": r.get("title", ""),
                "journal": r.get("journal", ""),
                "year": r.get("year", ""),
                "score": round(score, 3),
                "matched_tokens": matched
            })

    scored.sort(key=lambda x: -x["score"])
    return scored[:3]

# ---------- Main ----------

def main():
    print("=" * 60)
    print("Phase 1.75: Search for Replacement Citations")
    print("=" * 60)

    # Load Phase 1.5 report
    report = load_json(REPORT_PATH)
    mismatches = report.get("mismatches", [])
    weak_matches = report.get("weak_matches", [])

    print(f"\nMISMATCH edges: {len(mismatches)}")
    print(f"WEAK_MATCH edges: {len(weak_matches)}")
    print(f"Total: {len(mismatches) + len(weak_matches)}")

    # Load all edges for full context
    print("\nLoading module files for edge context...")
    all_edges_map = load_all_edges()

    # Build work list
    work_items = []

    for m in mismatches:
        pmid = m.get("pmid")
        doi = m.get("doi")
        module = m["module"]
        edge_str = m["edge"]
        key = f"{module}::{edge_str.replace(' -> ', '->')}"
        edge = all_edges_map.get(key)
        if edge:
            work_items.append({
                "status": "MISMATCH",
                "current_id": pmid or doi,
                "current_id_type": "PMID" if pmid else "DOI",
                "current_title": m.get("article_title", ""),
                "current_score": m.get("score", 0),
                "module": module,
                "edge_str": edge_str,
                "edge": edge,
                "prior_confidence": m.get("prior_confidence", "high")
            })

    for w in weak_matches:
        pmid = w.get("pmid")
        doi = w.get("doi")
        module = w["module"]
        edge_str = w["edge"]
        key = f"{module}::{edge_str.replace(' -> ', '->')}"
        edge = all_edges_map.get(key)
        if edge:
            work_items.append({
                "status": "WEAK_MATCH",
                "current_id": pmid or doi,
                "current_id_type": "PMID" if pmid else "DOI",
                "current_title": w.get("article_title", ""),
                "current_score": w.get("score", 0),
                "module": module,
                "edge_str": edge_str,
                "edge": edge
            })

    print(f"\nWork items loaded: {len(work_items)}")

    # Group by unique PMID/DOI for dedup stats
    mismatch_groups = defaultdict(list)
    for item in work_items:
        if item["status"] == "MISMATCH":
            mismatch_groups[item["current_id"]].append(item)
    weak_groups = defaultdict(list)
    for item in work_items:
        if item["status"] == "WEAK_MATCH":
            weak_groups[item["current_id"]].append(item)

    print(f"Unique bad PMIDs/DOIs to replace: {len(mismatch_groups)}")
    print(f"Unique weak PMIDs/DOIs to check: {len(weak_groups)}")

    # Search for each edge
    print("\n--- Searching for candidates ---\n")
    all_candidate_pmids = set()
    results = []

    for i, item in enumerate(work_items):
        edge = item["edge"]
        tag = item["status"]
        edge_str = item["edge_str"]
        module = item["module"]
        print(f"[{i+1}/{len(work_items)}] {tag} | {module} | {edge_str[:60]}")

        # PubMed search
        candidates, queries_tried = search_for_edge(edge, all_candidate_pmids)

        # CrossRef fallback if no PubMed candidates
        if not candidates:
            print(f"  No PubMed candidates. Trying CrossRef...")
            time.sleep(CROSSREF_DELAY)
            candidates = crossref_fallback(edge)
            if candidates:
                print(f"  Found {len(candidates)} CrossRef candidate(s)")

        if candidates:
            print(f"  Found {len(candidates)} candidate(s). Best: {candidates[0]['id']} (score={candidates[0]['score']})")
            for c in candidates:
                if c["type"] == "PMID":
                    all_candidate_pmids.add(c["id"])
        else:
            print(f"  No candidates found (tried {len(queries_tried)} queries)")

        # Store result
        edge_id = f"{module.replace('.json', '')}::{edge.get('source_node', '')}->{edge.get('target_node', '')}"
        results.append({
            "edge_id": edge_id,
            "module": module,
            "source_node": edge.get("source_node", ""),
            "target_node": edge.get("target_node", ""),
            "edge_type": edge.get("edge_type", ""),
            "temporal_range": edge.get("temporal_range", ""),
            "current_id": item["current_id"],
            "current_id_type": item["current_id_type"],
            "current_title": item["current_title"],
            "phase1_5_status": item["status"],
            "phase1_5_score": item["current_score"],
            "candidates": [
                {"rank": ci+1, **c} for ci, c in enumerate(candidates)
            ],
            "queries_tried": len(queries_tried),
            "action": ""
        })

    # ---------- Generate outputs ----------

    # Stats
    mismatch_with_cand = sum(1 for r in results if r["phase1_5_status"] == "MISMATCH" and r["candidates"])
    mismatch_no_cand = sum(1 for r in results if r["phase1_5_status"] == "MISMATCH" and not r["candidates"])
    weak_with_cand = sum(1 for r in results if r["phase1_5_status"] == "WEAK_MATCH" and r["candidates"])
    weak_no_cand = sum(1 for r in results if r["phase1_5_status"] == "WEAK_MATCH" and not r["candidates"])
    total_pmid_cands = sum(1 for r in results for c in r["candidates"] if c["type"] == "PMID")
    total_doi_cands = sum(1 for r in results for c in r["candidates"] if c["type"] == "DOI")

    print("\n" + "=" * 60)
    print("Phase 1.75 Summary")
    print("=" * 60)
    print(f"  Mismatch edges with candidates:     {mismatch_with_cand}")
    print(f"  Mismatch edges without candidates:   {mismatch_no_cand}")
    print(f"  Weak match edges with candidates:    {weak_with_cand}")
    print(f"  Weak match edges without candidates: {weak_no_cand}")
    print(f"  Total candidate PMIDs proposed:      {total_pmid_cands}")
    print(f"  Total candidate DOIs proposed:       {total_doi_cands}")

    # Write JSON
    print(f"\nWriting {JSON_OUT}...")
    json_output = {
        "generated": "2026-03-17",
        "stats": {
            "mismatch_with_candidates": mismatch_with_cand,
            "mismatch_no_candidates": mismatch_no_cand,
            "weak_with_candidates": weak_with_cand,
            "weak_no_candidates": weak_no_cand,
            "total_pmid_candidates": total_pmid_cands,
            "total_doi_candidates": total_doi_cands
        },
        "edges": results
    }
    save_json(JSON_OUT, json_output)

    # Write Markdown
    print(f"Writing {MD_OUT}...")
    write_markdown(results, mismatch_with_cand, mismatch_no_cand, weak_with_cand, weak_no_cand, total_pmid_cands, total_doi_cands)

    print("\nDone.")

def write_markdown(results, mismatch_with_cand, mismatch_no_cand, weak_with_cand, weak_no_cand, total_pmid_cands, total_doi_cands):
    """Write the human-readable review document."""
    lines = []
    lines.append("# Citation Repair Candidates — Phase 1.75\n")
    lines.append(f"Generated: 2026-03-17")

    mismatch_results = [r for r in results if r["phase1_5_status"] == "MISMATCH"]
    weak_results = [r for r in results if r["phase1_5_status"] == "WEAK_MATCH"]

    lines.append(f"Edges reviewed: {len(results)} ({len(mismatch_results)} mismatch + {len(weak_results)} weak match)")
    lines.append(f"Candidates found: {sum(1 for r in results if r['candidates'])}")
    lines.append(f"No candidate found: {sum(1 for r in results if not r['candidates'])}")
    lines.append("")
    lines.append("## How to Use This Document\n")
    lines.append("Review each row. For each edge, mark your decision in the **Action** column:")
    lines.append("- **ACCEPT n** — use candidate n (e.g., ACCEPT 1)")
    lines.append("- **KEEP** — retain the current citation (for weak matches that are acceptable)")
    lines.append("- **ARCHIVE** — downgrade to institutional_archive (no good PMID exists)")
    lines.append("- **DELETE** — remove the edge entirely (relationship is unverifiable)")
    lines.append("")
    lines.append("---\n")

    # MISMATCH section: group by current bad PMID
    lines.append("## MISMATCH Edges (Priority)\n")

    mismatch_by_pmid = defaultdict(list)
    for r in mismatch_results:
        mismatch_by_pmid[r["current_id"]].append(r)

    row_num = 0
    for current_id, edges in sorted(mismatch_by_pmid.items(), key=lambda x: -len(x[1])):
        current_title = edges[0]["current_title"][:80]
        lines.append(f'### {edges[0]["current_id_type"]} {current_id} — currently cites: "{current_title}"\n')
        lines.append(f"Affects {len(edges)} edge(s):\n")
        lines.append("| # | Edge | Module | Relationship Claimed | Candidate 1 | Candidate 2 | Candidate 3 | Action |")
        lines.append("|---|------|--------|---------------------|-------------|-------------|-------------|--------|")

        for r in edges:
            row_num += 1
            edge_str = f"{r['source_node']} -> {r['target_node']}"
            rel = f"{r['edge_type']} {r['temporal_range']}"

            cand_cells = []
            for ci in range(3):
                if ci < len(r["candidates"]):
                    c = r["candidates"][ci]
                    cand_cells.append(f'{c["type"]} {c["id"]} — "{c["title"][:50]}" {c["journal"]} {c["year"]} (score: {c["score"]})')
                else:
                    cand_cells.append("—")

            lines.append(f"| {row_num} | {edge_str} | {r['module']} | {rel} | {cand_cells[0]} | {cand_cells[1]} | {cand_cells[2]} | |")

        lines.append("")

    # WEAK_MATCH section
    lines.append("---\n")
    lines.append("## WEAK_MATCH Edges (Secondary)\n")
    lines.append("| # | Edge | Module | Current PMID/DOI | Current Article Title | Score | Candidate 1 (if better found) | Action |")
    lines.append("|---|------|--------|------------------|-----------------------|-------|-------------------------------|--------|")

    row_num = 0
    for r in weak_results:
        row_num += 1
        edge_str = f"{r['source_node']} -> {r['target_node']}"
        current_title = r["current_title"][:50]
        cand1 = "—"
        if r["candidates"]:
            c = r["candidates"][0]
            cand1 = f'{c["type"]} {c["id"]} — "{c["title"][:40]}" {c["journal"]} {c["year"]} (score: {c["score"]})'

        lines.append(f"| {row_num} | {edge_str} | {r['module']} | {r['current_id']} | {current_title} | {r['phase1_5_score']} | {cand1} | |")

    lines.append("")

    # No candidates found
    no_cand = [r for r in results if not r["candidates"]]
    if no_cand:
        lines.append("---\n")
        lines.append("## No Candidates Found\n")
        lines.append("These edges had zero PubMed or CrossRef results above the 0.20 threshold.")
        lines.append("Recommended action: downgrade to `institutional_archive` or delete.\n")
        lines.append("| # | Edge | Module | Relationship Claimed | Current Bad PMID/DOI | Queries Tried |")
        lines.append("|---|------|--------|---------------------|---------------------|---------------|")

        for ni, r in enumerate(no_cand, 1):
            edge_str = f"{r['source_node']} -> {r['target_node']}"
            rel = f"{r['edge_type']} {r['temporal_range']}"
            lines.append(f"| {ni} | {edge_str} | {r['module']} | {rel} | {r['current_id']} | {r['queries_tried']} |")

        lines.append("")

    # Summary
    lines.append("---\n")
    lines.append("## Summary Statistics\n")
    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    lines.append(f"| Mismatch edges with candidates | {mismatch_with_cand} |")
    lines.append(f"| Mismatch edges without candidates | {mismatch_no_cand} |")
    lines.append(f"| Weak match edges with better candidates | {weak_with_cand} |")
    lines.append(f"| Weak match edges — no improvement | {weak_no_cand} |")
    lines.append(f"| Total candidate PMIDs proposed | {total_pmid_cands} |")
    lines.append(f"| Total candidate DOIs proposed | {total_doi_cands} |")
    lines.append("")

    with open(MD_OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

if __name__ == "__main__":
    main()
