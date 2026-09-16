from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Select, select

from db.db import SessionDep
from models.journal_book import JournalBook
from models.user import User
from schemas.journal_book import JournalBookCreate, JournalBookPublic, JournalBookUpdate
from security.dependencies import get_current_user


router = APIRouter()


# get all books
@router.get("/", response_model=list[JournalBookPublic])
async def get_journal_books(
    user: Annotated[User, Depends(get_current_user)], db: SessionDep
):
    result = await db.scalars(
        Select(JournalBook).where(
            JournalBook.user_id == user.id, JournalBook.deleted_at.is_(None)
        ),
    )
    return result.all()


@router.post("/", response_model=JournalBookPublic, status_code=201)
async def create_journal_book(
    payload: JournalBookCreate,
    user: Annotated[User, Depends(get_current_user)], db: SessionDep
):
    new_journal_book = JournalBook(user_id=user.id, **payload.model_dump())
    db.add(new_journal_book)
    await db.commit()

    return new_journal_book
    

@router.get("/{book_id}", response_model=JournalBookPublic)
async def get_journal_book_by_id(
    book_id: str,
    user: Annotated[User, Depends(get_current_user)], db: SessionDep
):
    journal_book = await db.get(JournalBook, book_id)
    if journal_book:
        if journal_book.user_id == user.id and journal_book.deleted_at == None:
            return journal_book
    raise HTTPException(status_code=404, detail="Journal book not found")


@router.patch("/{book_id}", response_model=JournalBookPublic)
async def update_journal_book_by_id(
    book_id: str,
    payload: JournalBookUpdate,
    user: Annotated[User, Depends(get_current_user)], db: SessionDep

):
    book = await db.scalar(
        select(JournalBook).where(
            JournalBook.id == book_id,
            JournalBook.user_id == user.id,
            JournalBook.deleted_at.is_(None)
        )
    )

    if book is None:
        raise HTTPException(404, detail="Journal book not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(book, field, value)

    await db.flush()
    return book

@router.delete("/{book_id}", status_code=204)
async def delete_journal_book(
    book_id: str,
    user: Annotated[User, Depends(get_current_user)], db: SessionDep
):
    book = await db.scalar(select(JournalBook).where(JournalBook.id == book_id, JournalBook.user_id == user.id, JournalBook.deleted_at == None))
    if book:
        book.deleted_at = datetime.now(timezone.utc)

        db.add(book)
        await db.commit()
        return {"detail": "deleted successfully"}
    raise HTTPException(404, detail="Journal book not found")

    


    
