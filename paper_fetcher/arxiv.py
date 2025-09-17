import requests
from xml.etree import ElementTree

def fetch_arxiv(query: str, limit: int = 10):
    url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={limit}'
    r = requests.get(url)
    root = ElementTree.fromstring(r.content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    papers = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.strip()
        summary = entry.find('atom:summary', ns).text.strip()
        link = entry.find('atom:id', ns).text.strip()
        authors = entry.findall('atom:author', ns)
        authors_list = [{"name": a.find('atom:name', ns).text, "email": None} for a in authors]

        papers.append({
            "title": title,
            "abstract": summary,
            "authors": authors_list,
            "year": None,  # ArXiv XML doesn't always include year cleanly
            "url": link,
            "keywords": [],
            "doi": None,
            "pdf_url": link.replace("abs", "pdf") + ".pdf"
        })
    return papers
