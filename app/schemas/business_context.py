from pydantic import BaseModel, Field, field_validator

MAX_FIELD_LENGTH = 300

_INJECTION_PREFIXES = ("ignore ", "disregard ", "forget ", "system:")


class BusinessContextCreate(BaseModel):

    industry: str = Field(min_length=1, max_length=MAX_FIELD_LENGTH)
    ideal_customer: str = Field(min_length=1, max_length=MAX_FIELD_LENGTH)
    product: str = Field(min_length=1, max_length=MAX_FIELD_LENGTH)

    @field_validator("industry", "ideal_customer", "product", mode="before")
    @classmethod
    def sanitize(cls, v):
        if not isinstance(v, str):
            raise ValueError("Must be a string")
        v = v.strip()
        if any(v.lower().startswith(p) for p in _INJECTION_PREFIXES):
            raise ValueError("Invalid input")
        return v
