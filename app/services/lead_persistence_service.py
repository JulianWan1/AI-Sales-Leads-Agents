from sqlalchemy.orm import Session
from app.models.lead import Lead
from app.services.logger import logger

_LEAD_COLUMNS = {c.key for c in Lead.__table__.columns}


def save_leads(db: Session, leads: list) -> list:
    saved = []
    for lead_data in leads:
        existing = db.query(Lead).filter(Lead.company == lead_data.get("company")).first()
        if existing:
            for k, v in lead_data.items():
                if k in _LEAD_COLUMNS and k not in ("id", "created_at", "status"):
                    setattr(existing, k, v)
            saved.append({**lead_data, "id": existing.id})
        else:
            filtered = {k: v for k, v in lead_data.items() if k in _LEAD_COLUMNS}
            lead = Lead(**filtered)
            db.add(lead)
            db.flush()
            saved.append({**lead_data, "id": lead.id})
    db.commit()
    logger.info(f"Saved/updated {len(saved)} leads to database")
    return saved
