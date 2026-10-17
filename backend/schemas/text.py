from pydantic import BaseModel
from typing import Literal

class TextCreate(BaseModel):
    level: Literal["A2","B1","B2"]
    theme: str
    min_words: int
    max_words: int

class ResponseText(BaseModel):
    title: str
    text: str 