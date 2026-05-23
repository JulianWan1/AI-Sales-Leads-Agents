from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class Lead(Base):

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    company = Column(String, nullable=False)
    contact = Column(String)
    role = Column(String)

    interest = Column(String)

    estimated_budget = Column(Integer)

    company_summary = Column(Text)

    specialization = Column(Text)

    detected_industry = Column(String)

    research_confidence = Column(String)

    priority = Column(String)

    budget_signal = Column(String)

    purchase_likelihood = Column(String)

    qualification_signals = Column(Text)

    recommended_sales_angle = Column(Text)

    lead_score = Column(Integer)

    score_reasoning = Column(Text)

    outreach_strategy = Column(Text)

    conversation_starter = Column(Text)

    likely_objections = Column(Text)

    recommended_next_action = Column(Text)

    sources = Column(JSON)

    status = Column(String, default="new")

    source = Column(String, default="manual")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
