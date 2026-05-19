from sqlalchemy.orm import Session

from app.models.business_context import BusinessContext


def create_business_context(db: Session, context_data: dict):

    context = BusinessContext(**context_data)

    db.add(context)

    db.commit()

    db.refresh(context)

    return context


def get_latest_business_context(db: Session):

    return db.query(BusinessContext).order_by(BusinessContext.created_at.desc()).first()
