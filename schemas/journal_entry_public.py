

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from schemas.journal_book import JournalBookPublic


class JournalEntryPublic(BaseModel):
    id: str
    journal_book: JournalBookPublic
    title: Annotated[str | None, Field(max_length=255)]
    content: str
    modd: int | None
    created_at: datetime



class JournalEntryCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)


    journal_book_id: str
    title: Annotated[str | None, Field(max_length=255)]
    content: str
    mood: int | None

class JournalEntryUpdate(BaseModel):
    journal_book_id: str | None = None
    title: Annotated[str | None, Field(max_length=255)] = None
    content: str | None = None
    mood: int | None = None