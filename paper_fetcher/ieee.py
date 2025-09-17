import requests
from typing import List, Dict

IEEE_API_KEY = "h4vksqfudhumvu46jrxvvvuv"
BASE_URL = "http://ieeexploreapi.ieee.org/api/v1/search/articles"

def fetch_ieee(query: str, limit: int = 10, open_access_only: bool = False) -> List[Dict]:
    params = {
        "apikey": IEEE_API_KEY,
        "format": "json",
        "max_records": limit,
        "start_record": 1,
        "sort_field": "article_title",
        "sort_order": "asc",
        "querytext": query
    }
    if open_access_only:
        params["openAccess"] = "true"
    
    resp = requests.get(BASE_URL, params=params)
    resp.raise_for_status()
    data = resp.json()
    
    papers = []
    for item in data.get("articles", []):
        papers.append({
            "title": item.get("articleTitle"),
            "abstract": item.get("abstract"),
            "authors": [{"name": a, "email": None} for a in item.get("authors", [])],
            "year": item.get("publicationYear"),
            "url": item.get("htmlUrl"),
            "keywords": item.get("indexTerms", {}).get("ieee_terms", []) or [],
            "doi": item.get("doi"),
            "pdf_url": item.get("pdfUrl"),
            "source": "IEEE Xplore (Open Access)" if open_access_only else "IEEE Xplore"
        })
    return papers
