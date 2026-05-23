from pydantic import BaseModel
from typing import List


class Lead(BaseModel):

    company: str
    contact: str
    role: str
    interest: str

    budget_signal: str

    company_summary: str
    specialization: str
    detected_industry: str

    estimated_budget: int

    research_confidence: str

    purchase_likelihood: str

    qualification_signals: List[str]

    recommended_sales_angle: str

    lead_score: int

    priority: str

    score_reasoning: str

    outreach_strategy: str
    conversation_starter: str

    likely_objections: List[str]

    recommended_next_action: str

    sources: List[str]


class LeadList(BaseModel):

    leads: List[Lead]
