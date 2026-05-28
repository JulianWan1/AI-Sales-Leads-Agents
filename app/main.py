from fastapi import FastAPI

from app.api.business_context import router as business_router
from app.api.outreach_strategy import router as strategy_router
from app.api.leads import router as leads_router
from app.db.init_db import init_db

app = FastAPI()

init_db()

app.include_router(business_router)
app.include_router(strategy_router)
app.include_router(leads_router, prefix="/leads", tags=["leads"])


@app.get("/")
def root():
    return {"status": "running"}
