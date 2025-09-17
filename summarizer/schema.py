# backend/summarizer/schema.py
from pydantic import BaseModel
from typing import List

class ProcessStep(BaseModel):
    step: str
    mechanism: str
    advantages: str
    disadvantages: str

class Variables(BaseModel):
    dependent: List[str]
    independent: List[str]
    mediating: List[str]
    moderating: List[str]

class PaperSummary(BaseModel):
    title: str
    authors: List[str]
    keywords: List[str]
    method_model: str
    goal_problem: str
    components: List[str]
    process: List[ProcessStep]
    variables: Variables
    inputs: List[str]
    outputs: List[str]
    features: List[str]
    contribution_value: str
    positive_impacts: List[str]
    negative_impacts: List[str]
    critical_analysis: str
    tools_used: List[str]
    paper_structure: str
    diagrams_flowcharts: str
