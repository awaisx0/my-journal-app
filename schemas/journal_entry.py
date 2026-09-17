

from datetime import datetime
from typing import Annotated
import uuid

from pydantic import BaseModel, ConfigDict, Field

from schemas.journal_book import JournalBookPublic


class JournalEntryPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    journal_book: JournalBookPublic
    title: Annotated[str | None, Field(max_length=255)]
    content: str
    mood: int | None
    created_at: datetime



class JournalEntryCreate(BaseModel):

    journal_book_id: uuid.UUID
    title: Annotated[str | None, Field(max_length=255)] = None
    content: str
    mood: int | None = None

class JournalEntryUpdate(BaseModel):
    journal_book_id: str | None = None
    title: Annotated[str | None, Field(max_length=255)] = None
    content: str | None = None
    mood: int | None = None