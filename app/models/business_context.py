from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class BusinessContext(Base):

    __tablename__ = "business_contexts"

    id = Column(Integer, primary_key=True, index=True)

    industry = Column(String, nullable=False)

    ideal_customer = Column(String, nullable=False)

    product = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
