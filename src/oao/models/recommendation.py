from pydantic import BaseModel


class Recommendation(BaseModel):
    summary: str
    details: list[str]