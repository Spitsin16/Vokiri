from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class ReviewAnswer(BaseModel):
    answer: Literal["again", "hard", "good"]