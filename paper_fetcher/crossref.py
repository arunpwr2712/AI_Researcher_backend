import requests
# backend/paper_fetcher/crossref.py

def fetch_crossref(query: str, limit: int = 10):
    url = "https://api.crossref.org/works"
    params = {"query": query, "rows": limit, "select": "title,author,DOI,URL,abstract"}
    r = requests.get(url, params=params)
    try:
        data = r.json()
    except Exception:
        return []  # Return empty list if response is not valid JSON
    items = data.get('message', {}).get('items', [])
    papers = []
    for item in items:
        papers.append({
            "title": item.get("title", [""])[0],
            "abstract": item.get("abstract", ""),  # Safe default
            "authors": [{"name": f"{au.get('given','')} {au.get('family','')}".strip()} for au in item.get("author", [])],
            "doi": item.get("DOI"),
            "url": item.get("URL"),
            "keywords": item.get("subject", []),
            "pdf_url": None
        })
    return papers
