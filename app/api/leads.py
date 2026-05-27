from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.lead import Lead

router = APIRouter()

VALID_STATUSES = {"new", "contacted", "replied", "qualified", "closed", "lost"}


class StatusUpdate(BaseModel):
    status: str


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
