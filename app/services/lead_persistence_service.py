from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.services.logger import logger

_LEAD_COLUMNS = {c.key for c in Lead.__table__.columns}
_UPSERT_EXCLUDED = {"id", "created_at", "status", "last_enriched_at"}


def save_leads(db: Session, leads: list, upsert: bool = False) -> list:
    saved = []
    for lead_data in leads:
        existing = db.query(Lead).filter(Lead.company == lead_data.get("company")).first()
        if existing:
            if not upsert:
                continue
            # Re-enrichment — update all fields except protected ones
            for k, v in lead_data.items():
                if k in _LEAD_COLUMNS and k not in _UPSERT_EXCLUDED:
                    setattr(existing, k, v)
            existing.last_enriched_at = datetime.now(timezone.utc)
            saved.append({**lead_data, "id": existing.id})
        else:
            filtered = {k: v for k, v in lead_data.items() if k in _LEAD_COLUMNS and k not in _UPSERT_EXCLUDED}
            lead = Lead(**filtered)
            db.add(lead)
            db.flush()
            saved.append({**lead_data, "id": lead.id})
    db.commit()
    logger.info(f"Saved/updated {len(saved)} leads to database")
    return saved
