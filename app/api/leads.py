from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.orchestrator_agent import orchestrate_pipeline
from app.api.outreach_strategy import clean_final_leads
from app.core.database import get_db
from app.models.lead import Lead
from app.services.business_context_service import get_latest_business_context
from app.services.lead_persistence_service import save_leads

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


STALE_DAYS = 30


@router.post("/re-enrich-stale")
def re_enrich_stale(db: Session = Depends(get_db)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=STALE_DAYS)
    effective_date = func.coalesce(Lead.last_enriched_at, Lead.created_at)
    stale_leads = db.query(Lead).filter(effective_date < cutoff).all()
    if not stale_leads:
        return {"message": "No stale leads found", "updated": 0}
    context = get_latest_business_context(db)
    if not context:
        return {"message": "No business context found", "updated": 0}
    discovered = [{"company": lead.company} for lead in stale_leads]
    pipeline = orchestrate_pipeline(context, discovered)
    updated = save_leads(db, clean_final_leads(pipeline["leads"]), upsert=True)
    return {"message": f"Re-enriched {len(updated)} leads", "updated": len(updated)}
