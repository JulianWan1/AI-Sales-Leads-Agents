import json

from app.db.database import SessionLocal
from app.models.lead import Lead
from app.services.logger import logger


def save_leads(leads):

    db = SessionLocal()

    try:

        for lead in leads:

            db_lead = Lead(
                company=lead.get("company"),
                contact=lead.get("contact"),
                role=lead.get("role"),
                interest=lead.get("interest"),
                estimated_budget=lead.get("estimated_budget"),
                purchase_likelihood=lead.get("purchase_likelihood"),
                qualification_signals=json.dumps(lead.get("qualification_signals", [])),
                recommended_sales_angle=lead.get("recommended_sales_angle"),
                lead_score=lead.get("lead_score"),
                score_reasoning=lead.get("score_reasoning"),
                outreach_strategy=lead.get("outreach_strategy"),
                conversation_starter=lead.get("conversation_starter"),
                likely_objections=json.dumps(lead.get("likely_objections", [])),
                recommended_next_action=lead.get("recommended_next_action"),
            )

            db.add(db_lead)

        db.commit()

        logger.info(f"Saved {len(leads)} leads to database")

    finally:
        db.close()
