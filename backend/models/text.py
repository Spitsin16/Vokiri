from backend.database import Base
from sqlalchemy import String, DateTime, Text, CheckConstraint, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AllText(Base):
    __table_args__ = (CheckConstraint("level IN ('A2', 'B1', 'B2')",name="ck_all_texts_level",),)
    __tablename__ = ("all_texts")

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    theme: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[str] = mapped_column(String)
    target_words: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    word_count: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,default=utc_now)

class UserText(Base):
    __tablename__ = ("user_texts")
    __table_args__ = (UniqueConstraint("user_id","text_id",name="uq_user_text_user_text",),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    text_id: Mapped[int] = mapped_column(ForeignKey("all_texts.id",ondelete="CASCADE"),nullable=False)




