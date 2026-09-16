from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from db.db import Base
if TYPE_CHECKING:
    from models.journal_book import JournalBook


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("journal_books.id"))
    title: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    mood: Mapped[int | None] = mapped_column(SmallInteger())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    journal_book: Mapped["JournalBook"] = relationship(back_populates="entries")
    
    


