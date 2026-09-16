

from datetime import datetime
from typing import Annotated
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=72)]


class UserLogin(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=72)]


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    is_email_verified: bool
    created_at: datetime

