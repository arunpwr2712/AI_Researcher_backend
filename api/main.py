
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, APIRouter
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from typing import List
from chat_with_pdfs.chat_with_pdf import chat_with_pdf
#from paper_fetcher.ieee import fetch_ieee
#from paper_fetcher.semantic_scholar import fetch_semantic
from paper_fetcher.crossref import fetch_crossref
from paper_fetcher.arxiv import fetch_arxiv
from paper_fetcher.core_api import fetch_core
from summarizer.summarizer import analyze_with_gemini
from cache.cache_manager import get_cached_summary, set_cached_summary, generate_key,clear_cache_file
from pdf_parser.pdf_handler import download_pdf, parse_and_cleanup
from summary_to_table.json_to_word import json_to_word

import os, shutil
import re
import uvicorn




app = FastAPI()

# Generic endpoint to serve any local PDF file

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000", "https://researcher-ai.netlify.app/"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


def clean_text(text):
    text = re.sub(r'\s+', ' ', text)     # Remove excessive whitespace
    text = re.sub(r'[^a-zA-Z0-9\s.,]', '', text)  # Keep alpha-numeric and basic punctuations
    return text.strip()

@app.get("/ping")
async def ping():
    return {"status": "ready"}



@app.get("/")
async def root():
    return {"message": "Survey‑AI Backend is live"}



class RefreshFlag(BaseModel):
    flag: str

@app.post("/refresh")
async def receive_refresh(flag: RefreshFlag):
    # Perform any action you like (e.g., reset session, log, etc.)
    # print(f"Received refresh flag: {flag.flag}")

    return {"status": "ok"}


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UploadPDFsRequest(BaseModel):
    # For file uploads, Pydantic models are not used, so keep as is
    pass

@app.post("/upload_pdfs/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    saved_files = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file_path)

    return {"status": "success", "uploaded_files": saved_files}


def fetch_all(query, limit, include_private: bool = False):

    return (
        # fetch_semantic(query, limit) +
        fetch_crossref(query, limit) +
        fetch_arxiv(query, limit) +
        fetch_core(query, limit) 
        # fetch_ieee(query, limit, open_access_only=not include_private)
    )




class ChatPDFsRequest(BaseModel):
    user_query: str

@app.post("/chat_pdfs/")
async def chat_pdfs(request: ChatPDFsRequest):
    # Load summaries
    response = chat_with_pdf(request.user_query)
    return {"answer": response}






@app.get("/analyze/")
async def analyze(query: str = Query(None), limit_per_source: int = Query(5),  include_private: bool = Query(False, description="Toggle private IEEE access"), source: str = Query("scraping")):
    if source == "uploads":
    # Process all files in uploads folder
        for file_name in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, file_name)
            text = parse_and_cleanup(file_path)
            paper = {
            "title": file_name,
            "pdfurl": file_path,
            "url": None,
            "year": None
        }
            full_entry = { **paper, "full_text": text }  # include text for analysis
            # result = analyze_with_gemini(full_entry)  # returns dict matching PaperSummary
            summary_obj = analyze_with_gemini(full_entry)
            summary_dict = summary_obj.model_dump()
            summary_dict["url"] = paper.get("url")
            summary_dict["pdfurl"] = paper.get("pdf_url")
            summary_dict["year"] = paper.get("year")
            paper["summary"] = summary_dict
            # Now we can cache the full dict (no need to add 'summary' separately)
            set_cached_summary(file_name, paper["summary"], paper)
            paper.update(paper["summary"])
        
        json_to_word()
        clear_cache_file()

        return {
            "status": "success",
            "source": "uploads",
            "summaries": [paper],
            "docx_url": "/download/paper_summary.docx",
            "pdf_url": "/download/paper_summary.pdf"
        }

    
    else:
        papers = fetch_all(query, limit_per_source)
        if not papers:
            raise HTTPException(404, "No papers found")

        for paper in papers:
            key = generate_key(paper)
            cached = get_cached_summary(key)
            if cached:
                paper['summary'] = cached['summary']
                continue

            text = None
            if paper.get('pdf_url'):
                try:
                    pdf_path = download_pdf(paper['pdf_url'], key)
                    text = parse_and_cleanup(pdf_path)
                except Exception:
                    text = paper.get('abstract', "")
            else:
                text = paper.get('abstract') or ""
                text = clean_text(text)
            
            full_entry = { **paper, "full_text": text }  # include text for analysis
            # result = analyze_with_gemini(full_entry)  # returns dict matching PaperSummary
            summary_obj = analyze_with_gemini(full_entry)
            summary_dict = summary_obj.model_dump()
            summary_dict["url"] = paper.get("url")
            summary_dict["pdfurl"] = paper.get("pdf_url")
            summary_dict["year"] = paper.get("year")
            paper["summary"] = summary_dict
            # Now we can cache the full dict (no need to add 'summary' separately)
            set_cached_summary(key, paper["summary"], paper)
            paper.update(paper["summary"])
        json_to_word()
        clear_cache_file()

        return {
            "query": query,
            "results": papers,
            "docx_url": "/download/paper_summary.docx",
            "pdf_url": "/download/paper_summary.pdf"
        }





router = APIRouter()



from fastapi.responses import StreamingResponse

@app.get("/download_summary/")
async def download_summary(type: str = "pdf"):
    if type == "pdf":
        file_path = os.path.join(os.getcwd(), "paper_summary.pdf")
        media_type = "application/pdf"
        filename = "paper_summary.pdf"
    elif type == "docx":
        file_path = os.path.join(os.getcwd(), "paper_summary.docx")
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = "paper_summary.docx"
    else:
        raise HTTPException(status_code=400, detail="Invalid type parameter")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Summary {type.upper()} not found")
    def iterfile():
        with open(file_path, mode="rb") as file_like:
            yield from file_like
    return StreamingResponse(iterfile(), media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

