from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from websockets import PayloadTooBig

from db.db import SessionDep
from models.journal_book import JournalBook
from models.journal_entry import JournalEntry
from models.user import User
from schemas.journal_entry_public import JournalEntryPublic, JournalEntryCreate, JournalEntryUpdate
from security.dependencies import get_current_user


router = APIRouter()


@router.get("/{book_id}/entries", response_model=list[JournalEntryPublic])
async def get_entries(
    book_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    stmt = (
        select(JournalEntry)
        .join(JournalBook, JournalEntry.journal_book_id == JournalBook.id)
        .where(
            JournalEntry.journal_book_id == book_id, JournalBook.user_id == user.id, JournalEntry.deleted_at.is_(None)
        )
        .order_by(JournalEntry.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.scalars(stmt)
    entries = result.all()
    return entries

@router.post("/{book_id}/entries", response_model=JournalEntryPublic, status_code=201)
async def create_entry(
    payload: JournalEntryCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: SessionDep
):
    new_entry = JournalEntry(**payload.model_dump())
    db.add(new_entry)
    await db.commit()
    return new_entry


@router.get("/entries/{entry_id}", response_model=JournalEntryPublic, )
async def get_entry_by_id(
    entry_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: SessionDep

):
    entry = await db.get(JournalEntry, entry_id)
    if entry:
        return entry

    raise HTTPException(404, detail="Entry not found")


@router.patch("/entries{entry_id}", response_model=JournalEntryPublic)
async def update_entry_by_id(
    entry_id: str,
    payload: JournalEntryUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: SessionDep
):
    entry = await db.get(JournalEntry, entry_id)

    if entry:
        updated = payload.model_dump(exclude_unset=True)
        for field, value in updated.items():
            setattr(entry, field, value)
        await db.commit()
        return entry

    raise HTTPException(404, detail="Entry not found")

    

@router.delete("/{entry_id}", status_code=204)
async def delete_journal_book(
    entry_id: str,
    user: Annotated[User, Depends(get_current_user)], db: SessionDep
):
    entry = await db.scalar(select(JournalEntry).where(JournalBook.id == entry_id,))
    if entry:
        entry.deleted_at = datetime.now(timezone.utc)

        db.add(entry)
        await db.commit()
        return {"detail": "deleted successfully"}
    raise HTTPException(404, detail="Journal Entry not found")

    

    
