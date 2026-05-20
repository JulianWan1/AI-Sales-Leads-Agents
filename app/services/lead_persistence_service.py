import json

from sqlalchemy.orm import Session
from app.models.lead import Lead
from app.services.logger import logger


def save_leads(db: Session, leads: list):

    try:

        for lead_data in leads:

            lead = Lead(**lead_data)

            db.add(lead)

        db.commit()

        logger.info(f"Saved {len(leads)} leads to database")

    finally:
        db.close()
