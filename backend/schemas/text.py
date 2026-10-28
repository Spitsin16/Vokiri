from pydantic import BaseModel, Field
from typing import Literal

class TextCreate(BaseModel):
    level: Literal["A2","B1","B2"]
    theme: str
    min_words: int = Field(ge=50, le=1000)
    max_words: int = Field(ge=50, le = 1000)
    limit_words: int = Field(default=5,ge=0,le=10)

class ResponseText(BaseModel):
    title: str
    text: str 