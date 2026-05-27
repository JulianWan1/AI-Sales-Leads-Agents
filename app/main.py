from fastapi import FastAPI

from app.api.business_context import router as business_router
from app.api.lead_discovery import router as lead_router
from app.api.lead_enrichment import router as enrichment_router
from app.api.lead_scoring import router as scoring_router
from app.api.outreach_strategy import router as strategy_router
from app.api.leads import router as leads_router
from app.db.init_db import init_db

app = FastAPI()

init_db()

app.include_router(business_router)
app.include_router(lead_router)
app.include_router(enrichment_router)
app.include_router(scoring_router)
app.include_router(strategy_router)
app.include_router(leads_router, prefix="/leads", tags=["leads"])


@app.get("/")
def root():
    return {"status": "running"}
