from pydantic import BaseModel


class BusinessContextCreate(BaseModel):

    industry: str

    ideal_customer: str

    product: str
