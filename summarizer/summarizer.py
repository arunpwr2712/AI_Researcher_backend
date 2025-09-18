import os
import time
import json
from google import genai
from google.genai import types
from google.genai.errors import ServerError
from .schema import PaperSummary
from dotenv import load_dotenv
# backend/summarizer/summarizer.py

# Load API key from environment
load_dotenv()
#os.environ["GOOGLE_API_KEY"] = os.getenv("Gemini_API_KEY")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) 

prompt = """
You are a research assistant. Analyze the full text below and output a **pure JSON object** matching this schema (no extra text) provides a structured summary of the research paper. The output should be a JSON object with the following keys and their respective values:
The provides schema is:
{schema}

**Reference of paper in APA format**: research paper reference in APA format.
**DOI**: DOI of the paper.
**URL of the Reference**: 
**Title**: Title of the Paper
**Authors**: Authors Names and Emails
**Keywords**: Keywords in this Reference
**Method/Model**: The Name of the Current Solution (Technique/ Method/ Scheme/ Algorithm/ Model/ Tool/ Framework/ ... etc) - Just write the Name and a very small description about solution.
**Goal & Problem Statement**: The Goal (Objective) of this Solution & What is the problem that need to be solved in 2 accurate points.
**Components** (list major system components): What are the components of solution used int the paper?
**Process**: How the Problem has Solved in a single point within 30-50 words and provide a table-like bullet list showing step, mechanism, advantages, disadvantages:
**Variables**: which are used the solution/word. Find the variables implicitly and explicitly. Give only names without any description.
- Dependent:
- Independent:
- Mediating:
- Moderating:
**Inputs and Outputs**: Input and Output format precisely. Give only name without any description.
**Features of Solution**:
**Contribution & Value**: Contribution & The Value of This Work to the real world.
**Positive Impacts**: Positive Impact of this Solution in This Project Domain.
**Negative Impacts**: Negative Impact of this Solution in This Project Domain.
**Critical Analysis**: Analyze This Work by Critical Thinking.
**Tools Used**: The Tools That Assessed this Work.
**Paper Structure**: What is the Structure/format of this Paper.
**Diagrams/Flowcharts**: mention if present.
**Summary**: A medium-length summary paragraph synthesizing all points in 100-150 words.
---
Text:
{full_text}
"""


def remove_jsonschema_refs(schema):
    if isinstance(schema, dict):
        return {
            k: remove_jsonschema_refs(v)
            for k, v in schema.items()
            if not k.startswith("$")
        }
    elif isinstance(schema, list):
        return [remove_jsonschema_refs(item) for item in schema]
    else:
        return schema

def analyze_with_gemini(full_text: str) -> PaperSummary:
    schema_dict = PaperSummary.model_json_schema()
    schema_dict.pop("title", None)
    schema_dict = remove_jsonschema_refs(schema_dict)
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=types.Part.from_text(text = prompt.format(schema=schema_dict, full_text=full_text)),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema_dict
            ),
        )
    except Exception as e:
        print("Gemini API call failed:", repr(e))
        response = None
    
    if response is None or not getattr(response, 'text', None):
        response_json = {
            "title": "",
            "authors": [],
            "keywords": [],
            "method_model": "",
            "goal_problem": "",
            "components": [],
            "process": [],
            "variables": {
                "dependent": [],
                "independent": [],
                "mediating": [],
                "moderating": []
            },
            "inputs": [],
            "outputs": [],
            "features": [],
            "contribution_value": "",
            "positive_impacts": [],
            "negative_impacts": [],
            "critical_analysis": "Gemini API did not return a valid response.",
            "tools_used": [],
            "paper_structure": "",
            "diagrams_flowcharts": ""
        }
    else:
        try:
            response_json = json.loads(response.text)
        except Exception:
            print("Gemini API raw response:", repr(response.text))
            response_json = {
                "title": "",
                "authors": [],
                "keywords": [],
                "method_model": "",
                "goal_problem": "",
                "components": [],
                "process": [],
                "variables": {
                    "dependent": [],
                    "independent": [],
                    "mediating": [],
                    "moderating": []
                },
                "inputs": [],
                "outputs": [],
                "features": [],
                "contribution_value": "",
                "positive_impacts": [],
                "negative_impacts": [],
                "critical_analysis": "Gemini API did not return a valid response.",
                "tools_used": [],
                "paper_structure": "",
                "diagrams_flowcharts": ""
            }
    # Post-process variables to match expected format
    variables = response_json.get("variables", {})
    normalized_vars = {}
    for key in ["dependent", "independent", "mediating", "moderating"]:
        value = variables.get(key) or variables.get(key.capitalize()) or []
        if isinstance(value, str):
            value = [value]  # Convert string to single-item list
        elif not isinstance(value, list):
            value = []
        normalized_vars[key] = value
    response_json["variables"] = normalized_vars

    # Fix process field: ensure it's a list of dicts with required keys and string values
    process = response_json.get("process", [])
    fixed_process = []
    for item in process:
        if not isinstance(item, dict):
            continue
        for k in ["step", "mechanism", "advantages", "disadvantages"]:
            if k not in item:
                item[k] = ""
            if isinstance(item[k], list):
                item[k] = "; ".join(str(v) for v in item[k])
            if k == "step" and not isinstance(item[k], str):
                item[k] = str(item[k])
        fixed_process.append(item)
    response_json["process"] = fixed_process

    return PaperSummary.model_validate(response_json)

def analyze_with_gemini_with_retry(full_entry, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return analyze_with_gemini(full_entry)
        except ServerError as e:
            if "503" in str(e) and attempt < retries - 1:
                time.sleep(delay)
            else:
                raise




