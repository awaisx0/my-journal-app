

from datetime import datetime
from typing import Annotated
import uuid

from pydantic import BaseModel, ConfigDict, Field

from schemas.user import UserPublic


class JournalBookCreate(BaseModel):
    user: UserPublic
    name: Annotated[str, Field(max_length=50)]
    description: str | None
    emoji: str | None
    color_hex: str | None



class JournalBookPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    emoji: str | None
    color_hex: str | None
    is_archived: bool
    created_at: datetime


class JournalBookUpdate(BaseModel):
    name: str | None = None
    descripton: str | None = None
    emoji: str | None = None
    color_hex: str | None = None
    is_archived: bool | None = None

    
    