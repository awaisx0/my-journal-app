import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select

from db.db import SessionDep
from models.journal_book import JournalBook
from models.journal_entry import JournalEntry
from models.user import User
from schemas.journal_entry_public import JournalEntryCreate, JournalEntryPublic, JournalEntryUpdate
from security.dependencies import get_current_user


router = APIRouter()


@router.get("/{book_id}/entries", response_model=list[JournalEntryPublic])
async def get_entries(
    book_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    stmt = (
        select(JournalEntry)
        .join(JournalBook, JournalEntry.journal_book_id == JournalBook.id)
        .where(
            JournalEntry.journal_book_id == book_id,
            JournalBook.user_id == user.id,
            JournalEntry.deleted_at.is_(None),
        )
        .order_by(JournalEntry.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.scalars(stmt)
    return result.all()


@router.post("/{book_id}/entries", response_model=JournalEntryPublic, status_code=201)
async def create_entry(
    book_id: uuid.UUID,
    payload: JournalEntryCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: SessionDep,
):
    # Confirm the book exists AND belongs to the caller before letting them
    # write an entry into it. Without this check, any authenticated user
    # could pass any book_id in the URL and create entries inside someone
    # else's journal.
    book = await db.scalar(
        select(JournalBook).where(
            JournalBook.id == book_id,
            JournalBook.user_id == user.id,
            JournalBook.deleted_at.is_(None),
        )
    )
    if book is None:
        raise HTTPException(404, detail="Journal book not found")

    new_entry = JournalEntry(journal_book_id=book_id, **payload.model_dump())
    db.add(new_entry)
    await db.commit()
    return new_entry


@router.get("/entries/{entry_id}", response_model=JournalEntryPublic)
async def get_entry_by_id(
    entry_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: SessionDep,
):
    # JournalEntry has no user_id column of its own, so ownership can only
    # be checked by joining through its parent JournalBook - same reason
    # get_entries above joins instead of filtering on JournalEntry alone.
    entry = await db.scalar(
        select(JournalEntry)
        .join(JournalBook, JournalEntry.journal_book_id == JournalBook.id)
        .where(
            JournalEntry.id == entry_id,
            JournalBook.user_id == user.id,
            JournalEntry.deleted_at.is_(None),
        )
    )
    if entry is None:
        raise HTTPException(404, detail="Entry not found")
    return entry


@router.patch("/entries/{entry_id}", response_model=JournalEntryPublic)
async def update_entry_by_id(
    entry_id: uuid.UUID,
    payload: JournalEntryUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: SessionDep,
):
    entry = await db.scalar(
        select(JournalEntry)
        .join(JournalBook, JournalEntry.journal_book_id == JournalBook.id)
        .where(
            JournalEntry.id == entry_id,
            JournalBook.user_id == user.id,
            JournalEntry.deleted_at.is_(None),
        )
    )
    if entry is None:
        raise HTTPException(404, detail="Entry not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(entry, field, value)

    # commit (not just flush) so the write is actually finalized before the
    # response goes out - get_db_session's own commit runs only after the
    # response is already sent, which is too late for a client that reads
    # this data back immediately.
    await db.commit()
    return entry


@router.delete("/entries/{entry_id}", status_code=204)
async def delete_entry(
    entry_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: SessionDep,
):
    entry = await db.scalar(
        select(JournalEntry)
        .join(JournalBook, JournalEntry.journal_book_id == JournalBook.id)
        .where(
            JournalEntry.id == entry_id,
            JournalBook.user_id == user.id,
            JournalEntry.deleted_at.is_(None),
        )
    )
    if entry is None:
        raise HTTPException(404, detail="Entry not found")

    entry.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return {"detail": "deleted successfully"}
