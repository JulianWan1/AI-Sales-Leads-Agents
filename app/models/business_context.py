from pydantic import BaseModel


class BusinessContext(BaseModel):
    industry: str
    ideal_customer: str
    product: str
