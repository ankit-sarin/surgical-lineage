#!/usr/bin/env python3
"""PMID and DOI verification for V5 expansion edges."""

import time
import urllib.request
import xml.etree.ElementTree as ET
import ssl
import json

PMIDS = [
    "9465770", "10359266", "12296669", "12717368", "12946817", "12946818",
    "14606488", "14703738", "18286472", "18294269", "22136854", "22248679",
    "22770963", "25135240", "25135241", "26811046", "31944281", "32106907",
    "33421312", "37439820", "37601473", "37746597", "39257568"
]

EXPECTED = {
    "9465770":  {"surnames": ["Kocher", "Cushing", "Halsted"], "journal": "World J Surg"},
    "10359266": {"surnames": ["Brown"], "journal": "Plast Reconstr Surg"},
    "12296669": {"surnames": ["Naffziger", "Cushing", "California"], "journal": "Neurosurgery"},
    "12717368": {"surnames": ["Varco", "Najarian"], "journal": "Surgery"},
    "12946817": {"surnames": ["Zollinger"], "journal": "Am J Surg"},
    "12946818": {"surnames": ["Zollinger", "Ohio State"], "journal": "Am J Surg"},
    "14606488": {"surnames": ["Rhoads", "Barker"], "journal": "Proc Am Philos Soc"},
    "14703738": {"surnames": ["Sabiston"], "journal": "Ann Thorac Surg"},
    "18286472": {"surnames": ["Brennan"], "journal": "J Surg Oncol"},
    "18294269": {"surnames": ["Folkman"], "journal": "J Pediatr Surg"},
    "22136854": {"surnames": ["Thompson"], "journal": "Am Surg"},
    "22248679": {"surnames": ["Blalock", "Conte"], "journal": "J Thorac Cardiovasc Surg"},
    "22770963": {"surnames": ["Hunter", "Physick"], "journal": "J Am Coll Surg"},
    "25135240": {"surnames": ["Anderson", "Cox", "Spray"], "journal": "J Thorac Cardiovasc Surg"},
    "25135241": {"surnames": ["Reemtsma", "DeAnda"], "journal": "J Thorac Cardiovasc Surg"},
    "26811046": {"surnames": ["Stanford", "Holman", "Woo"], "journal": "Semin Thorac Cardiovasc Surg"},
    "31944281": {"surnames": ["Brennan", "Printz"], "journal": "Cancer"},
    "32106907": {"surnames": ["Ravitch"], "journal": "Am Surg"},
    "33421312": {"surnames": ["St. Mark's", "ASCRS"], "journal": "Dis Colon Rectum"},
    "37439820": {"surnames": ["Jackson"], "journal": "Ann Otol Rhinol Laryngol"},
    "37601473": {"surnames": ["Blair", "Brown"], "journal": "Plast Reconstr Surg"},
    "37746597": {"surnames": ["Scott", "Vanderbilt"], "journal": "Ann Surg Open"},
    "39257568": {"surnames": ["Bollinger", "Sabiston"], "journal": "Ann Surg"},
}

# Create an SSL context that doesn't verify (for corporate proxies)
ctx = ssl.create_default_context()


def fetch_pmid(pmid):
    """Fetch PubMed article data for a PMID."""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml&rettype=abstract"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'SurgicalLineageAtlas/1.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = resp.read()
            return data.decode('utf-8')
    except Exception as e:
        return f"ERROR: {e}"


def parse_article(xml_str):
    """Parse PubMed XML and extract key fields."""
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError:
        return None

    article = root.find('.//PubmedArticle')
    if article is None:
        return None

    result = {}

    # Title
    title_el = article.find('.//ArticleTitle')
    result['title'] = title_el.text if title_el is not None and title_el.text else ''
    # Handle mixed content in title (italic tags etc.)
    if title_el is not None:
        result['title'] = ''.join(title_el.itertext())

    # First author
    authors = article.findall('.//Author')
    if authors:
        last = authors[0].find('LastName')
        result['first_author'] = last.text if last is not None else 'N/A'
    else:
        result['first_author'] = 'N/A'

    # All authors
    all_authors = []
    for a in authors:
        last = a.find('LastName')
        if last is not None and last.text:
            all_authors.append(last.text)
    result['all_authors'] = all_authors

    # Journal
    journal = article.find('.//Journal/Title')
    result['journal'] = journal.text if journal is not None else 'N/A'

    # Journal abbreviation (ISOAbbreviation)
    journal_abbr = article.find('.//Journal/ISOAbbreviation')
    result['journal_abbr'] = journal_abbr.text if journal_abbr is not None else ''

    # Year
    year = article.find('.//PubDate/Year')
    if year is None:
        year = article.find('.//PubDate/MedlineDate')
    result['year'] = year.text[:4] if year is not None and year.text else 'N/A'

    # MeSH PersonalNameSubjectList
    mesh_names = []
    for pn in article.findall('.//PersonalNameSubjectList/PersonalNameSubject'):
        ln = pn.find('LastName')
        if ln is not None and ln.text:
            mesh_names.append(ln.text)
    result['mesh_persons'] = mesh_names

    return result


def check_surname_match(pmid, article_data, expected):
    """Check if any expected surname appears in article metadata."""
    if not article_data:
        return False, "N/A"

    search_text = ' '.join([
        article_data.get('title', ''),
        ' '.join(article_data.get('all_authors', [])),
        ' '.join(article_data.get('mesh_persons', [])),
    ]).lower()

    matches = []
    for surname in expected['surnames']:
        if surname.lower() in search_text:
            matches.append(surname)

    return len(matches) > 0, ', '.join(matches) if matches else 'NONE'


def main():
    results = []
    failed = []

    print("=== PMID VERIFICATION ===\n")
    print(f"{'PMID':<12}| {'Status':<8}| {'First Author':<16}| {'Journal':<30}| {'Year':<6}| Surname Match")
    print("-" * 110)

    for pmid in PMIDS:
        xml_str = fetch_pmid(pmid)
        time.sleep(0.4)  # Rate limit: 3/sec max

        if xml_str.startswith("ERROR:"):
            print(f"{pmid:<12}| {'FAIL':<8}| {'HTTP Error':<16}| {'N/A':<30}| {'N/A':<6}| {xml_str}")
            failed.append(pmid)
            continue

        article = parse_article(xml_str)
        if not article:
            print(f"{pmid:<12}| {'FAIL':<8}| {'Parse Error':<16}| {'N/A':<30}| {'N/A':<6}| No PubmedArticle in XML")
            failed.append(pmid)
            continue

        matched, match_str = check_surname_match(pmid, article, EXPECTED[pmid])
        status = "PASS" if matched else "FAIL"
        if not matched:
            failed.append(pmid)

        # Truncate journal name for display
        journal_display = article['journal_abbr'] or article['journal']
        if len(journal_display) > 28:
            journal_display = journal_display[:26] + '..'

        checkmark = " OK" if matched else " MISSING"
        print(f"{pmid:<12}| {status:<8}| {article['first_author']:<16}| {journal_display:<30}| {article['year']:<6}| {match_str}{checkmark}")

        results.append({
            'pmid': pmid,
            'status': status,
            'first_author': article['first_author'],
            'journal': article['journal_abbr'] or article['journal'],
            'year': article['year'],
            'title': article['title'],
            'surname_match': match_str,
            'all_authors': article['all_authors'],
            'mesh_persons': article['mesh_persons'],
        })

    print(f"\n{'='*110}")
    print(f"Total PMIDs checked: {len(PMIDS)}")
    print(f"Passed: {len(PMIDS) - len(failed)}")
    print(f"Failed: {len(failed)}")
    if failed:
        print(f"Failed PMIDs for manual review: {', '.join(failed)}")

    # Save results to JSON for reference
    with open('v5_pmid_verification_results.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        f.write('\n')

    # === DOI VERIFICATION (Task 3) ===
    print("\n\n=== DOI VERIFICATION ===\n")
    doi = "10.1007/s10029-009-0522-1"
    doi_url = f"https://doi.org/{doi}"

    # Check if DOI resolves
    try:
        req = urllib.request.Request(doi_url, headers={
            'User-Agent': 'SurgicalLineageAtlas/1.0',
            'Accept': 'application/json',
        })
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            status_code = resp.getcode()
            # Read content type
            content_type = resp.headers.get('Content-Type', '')
            body = resp.read().decode('utf-8')
            print(f"DOI {doi}: resolves (HTTP {status_code})")
            print(f"Content-Type: {content_type}")
            if 'json' in content_type:
                data = json.loads(body)
                print(f"Title: {data.get('title', 'N/A')}")
                print(f"Container: {data.get('container-title', 'N/A')}")
    except Exception as e:
        print(f"DOI {doi}: {e}")

    # Check PubMed for this DOI
    time.sleep(0.5)
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={doi}[doi]&retmode=json"
    try:
        req = urllib.request.Request(search_url, headers={'User-Agent': 'SurgicalLineageAtlas/1.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            id_list = data.get('esearchresult', {}).get('idlist', [])
            if id_list:
                print(f"DOI has associated PMID: {id_list[0]}")
                print(f"RECOMMENDATION: Upgrade evidence_type to PMID, citation to 'PMID: {id_list[0]}', locator to 'https://pubmed.ncbi.nlm.nih.gov/{id_list[0]}/'")
            else:
                print("DOI does NOT have an associated PMID in PubMed. Keeping as DOI citation.")
    except Exception as e:
        print(f"PubMed DOI lookup error: {e}")


if __name__ == '__main__':
    main()
