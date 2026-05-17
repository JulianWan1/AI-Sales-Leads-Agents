from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from app.db.database import Base


class Lead(Base):

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    company = Column(String)
    contact = Column(String)
    role = Column(String)

    interest = Column(String)

    estimated_budget = Column(Integer)
    purchase_likelihood = Column(String)

    qualification_signals = Column(Text)

    recommended_sales_angle = Column(Text)

    lead_score = Column(Integer)

    score_reasoning = Column(Text)

    outreach_strategy = Column(Text)

    conversation_starter = Column(Text)

    likely_objections = Column(Text)

    recommended_next_action = Column(Text)
