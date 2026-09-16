
from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from db.db import Base
if TYPE_CHECKING:
    from models.journal_entry import JournalEntry
    from models.user import User


class JournalBook(Base):
    __tablename__ = "journal_books"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True, ), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text())
    emoji: Mapped[str | None]
    color_hex: Mapped[str | None] = mapped_column(String(10))
    is_archived: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    owner: Mapped["User"] = relationship(back_populates="journal_books")
    entries: Mapped[list["JournalEntry"]] = relationship(back_populates="journal_book")


