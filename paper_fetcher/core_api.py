import requests

CORE_API_KEY = "1CYxuB5aoIWEh9dHT7nzmL3NgjvkGiOp"  # Replace this with your actual key

def fetch_core(query: str, limit: int = 10):
    url = "https://api.core.ac.uk/v3/search/works"
    headers = {
        "Authorization": f"Bearer {CORE_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "q": query,
        "page": 1,
        "pageSize": limit
    }

    r = requests.post(url, json=body, headers=headers)
    response = r.json()
    papers = []

    for item in response.get("results", []):
        paper = item.get("metadata", {})
        authors = paper.get("authors", [])
        papers.append({
            "title": paper.get("title", ""),
            "abstract": paper.get("abstract", ""),
            "authors": [{"name": a.get("name", ""), "email": None} for a in authors],
            "year": paper.get("publishedDate", "")[:4],
            "url": paper.get("url", ""),
            "keywords": paper.get("fieldsOfStudy", []),
            "doi": paper.get("doi", None),
            "pdf_url": paper.get("downloadUrl", None)
        })
    return papers
