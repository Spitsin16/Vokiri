from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr = Field(max_length=320)
    password: str = Field(min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=320)
    password: str = Field(min_length=8, max_length=128)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_active:bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str 

class AddWord(BaseModel):
    sense_id: int = Field(gt=0)
    preferred_translation_id: int | None = Field(default= None, gt=0)
    custom_translation: str | None = Field(default= None, max_length=255 ,min_length=1)


class DeleteWordResponse(BaseModel):
    source_sense_id: int
    is_active: bool 

