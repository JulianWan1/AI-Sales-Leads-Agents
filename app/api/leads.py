from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.lead import Lead

router = APIRouter()

VALID_STATUSES = {"new", "contacted", "replied", "qualified", "closed", "lost"}


class StatusUpdate(BaseModel):
    status: str


def _lead_to_dict(lead: Lead) -> dict:
    return {c.key: getattr(lead, c.key) for c in Lead.__table__.columns}


@router.get("/")
def list_leads(
    industry: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    score_min: int = 0,
    score_max: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(Lead)
    if industry:
        q = q.filter(Lead.detected_industry.ilike(f"%{industry}%"))
    if priority:
        q = q.filter(Lead.priority == priority)
    if status:
        q = q.filter(Lead.status == status)
    q = q.filter(Lead.lead_score.between(score_min, score_max))
    leads = q.order_by(Lead.created_at.desc()).all()
    return [_lead_to_dict(lead) for lead in leads]


@router.patch("/{lead_id}/status")
def update_lead_status(lead_id: int, payload: StatusUpdate, db: Session = Depends(get_db)):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
        )
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.status = payload.status
    db.commit()
    return {"id": lead_id, "status": payload.status}
