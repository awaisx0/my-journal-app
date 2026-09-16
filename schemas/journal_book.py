

from datetime import datetime
from typing import Annotated
import uuid

from pydantic import BaseModel, ConfigDict, Field



class JournalBookCreate(BaseModel):
    name: Annotated[str, Field(max_length=50)]
    description: str | None = None
    emoji: str | None = None
    color_hex: str | None = None



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
    description: str | None = None
    emoji: str | None = None
    color_hex: str | None = None
    is_archived: bool | None = None

    
    