from app.core.database import engine, Base

from app.models.lead import Lead
from app.models.business_context import BusinessContext

Base.metadata.create_all(bind=engine)

print("Tables created successfully.")
