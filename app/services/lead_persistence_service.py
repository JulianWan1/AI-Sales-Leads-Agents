from sqlalchemy.orm import Session
from app.models.lead import Lead
from app.services.logger import logger

_LEAD_COLUMNS = {c.key for c in Lead.__table__.columns}


def save_leads(db: Session, leads: list) -> list:
    saved = []
    for lead_data in leads:
        filtered = {k: v for k, v in lead_data.items() if k in _LEAD_COLUMNS}
        lead = Lead(**filtered)
        db.add(lead)
        db.flush()
        saved.append({**lead_data, "id": lead.id})
    db.commit()
    logger.info(f"Saved {len(saved)} leads to database")
    return saved
