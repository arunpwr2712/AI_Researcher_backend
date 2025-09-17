import os, requests
# from paper_fetcher import os as pf_os
from pdf_parser.parser import extract_text

TMP_DIR = os.path.join(os.path.dirname(__file__), '..', 'tmp')
os.makedirs(TMP_DIR, exist_ok=True)

def download_pdf(url: str, key: str) -> str:
    ext = 'pdf'
    path = os.path.join(TMP_DIR, f"{key}.{ext}")
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    with open(path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return path

def parse_and_cleanup(pdf_path: str) -> str:
    with open(pdf_path, 'rb') as f:
        raw = f.read()
    text = extract_text(raw)
    os.remove(pdf_path)
    return text