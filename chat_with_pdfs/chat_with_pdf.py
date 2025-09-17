import os
from google import genai
from google.genai import types
import pathlib
import re
from dotenv import load_dotenv
# backend/summarizer/summarizer.py

def clean_text(text):
    # text = re.sub(r'\s+', ' ', text)     # Remove excessive whitespace
    text = re.sub(r'[^a-zA-Z0-9\s.,]', '', text)  # Keep alpha-numeric and basic punctuations
    return text.strip()

# Load API key from environment
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
load_dotenv()
#os.environ["GOOGLE_API_KEY"] = os.getenv("Gemini_API_KEY")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) 
# client = genai.Client(api_key="AIzaSyDiEpn5p976VNSeNZw-EEB8mSp_R5ZjXiA") 
# client = genai.Client(api_key="AIzaSyDG7l3kcICM13ZtC_BNTiDOap0rPUzucxs")


# Retrieve and encode the PDF byte
file_path = os.path.join(os.getcwd(), "paper_summary.pdf")

def chat_with_pdf(user_query: str):
    prompt = f"""
You are an expert research assistant. 
Answer the question strictly based on the following structured research summaries provided in the document:

Use the pdf to answer. Always cite which paper(s) title the answer comes from.



Question: {user_query}
Answer:
"""
    response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=[
        types.Part.from_bytes(
            data=pathlib.Path(file_path).read_bytes(),
            mime_type='application/pdf',
        ),
        prompt])
    # print(response.text)

    return clean_text(response.text)

