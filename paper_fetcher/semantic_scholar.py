from semanticscholar import SemanticScholar

SCH = SemanticScholar()

def fetch_semantic(query: str, limit: int = 10):
    # results = SCH.search_paper(query=query, limit=limit,
    #     fields=['title','abstract','authors','year','url','openAccessPdf']
    # )
    results = SCH.search_paper(query=query, limit=limit,
        fields=['title','abstract','authors','year','url','openAccessPdf'],
        open_access_pdf=True
    )
    papers = []
    for p in results:
        # pdf_info = p.get('openAccessPdf')
        
        # print(p.openAccessPdf)
        papers.append({
            "title": p.title,
            "abstract": p.abstract,
            "authors": [{"name": a.name, "email": None} for a in p.authors],
            "year": p.year,
            "url": getattr(p, 'url', None),
            "keywords": [],
            "doi": getattr(p, 'doi', None),
            "pdf_url": p.openAccessPdf.url if p.openAccessPdf else None
        })
    return papers
