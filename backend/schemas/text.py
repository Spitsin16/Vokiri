from pydantic import BaseModel, Field, model_validator
from typing import Literal

class TextCreate(BaseModel):
    level: Literal["A2","B1","B2"]
    theme: str = Field(min_length=2, max_length=150)
    min_words: int = Field(ge=50, le=1000)
    max_words: int = Field(ge=50, le = 1000)
    limit_words: int = Field(default=5, ge=1, le=10)

    @model_validator(mode="after")
    def validate_word_range(self):
        if self.min_words > self.max_words:
            raise ValueError(
                "min_words must be less than or equal to max_words"
            )
        return self

class ResponseText(BaseModel):
    title: str
    text: str

class GeneratedText(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    text: str = Field(min_length=1)