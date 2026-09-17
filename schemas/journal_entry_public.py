import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class JournalEntryPublic(BaseModel):
    # from_attributes lets this be built straight from a JournalEntry ORM
    # object (attribute access) instead of only from a dict - it belongs on
    # the *response* schema, not on the request schema below.
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    journal_book_id: uuid.UUID
    title: str | None
    content: str
    mood: int | None
    created_at: datetime


class JournalEntryCreate(BaseModel):
    # journal_book_id is deliberately not a field here: which book an entry
    # belongs to comes from the {book_id} in the URL and is ownership-checked
    # there (see create_entry), never from client-supplied body data.
    title: Annotated[str | None, Field(max_length=255)] = None
    content: str
    # PRD specifies mood as 0-10; the DB column (SmallInteger) only rejects
    # values outside 16-bit range, so the 0-10 rule has to be enforced here.
    mood: Annotated[int | None, Field(ge=0, le=10)] = None


class JournalEntryUpdate(BaseModel):
    # journal_book_id intentionally omitted too - moving an entry to a
    # different book isn't supported, so there's no field a client could
    # use to reassign it to a book they don't own.
    title: Annotated[str | None, Field(max_length=255)] = None
    content: str | None = None
    mood: Annotated[int | None, Field(ge=0, le=10)] = None
