from backend.database import Base
from sqlalchemy import DateTime, Boolean, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class UserWord(Base):
    __tablename__ = "user_words"

    __table_args__ = (UniqueConstraint("user_id", "source_sense_id",name="uq_user_word_user_sense",),)

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    source_sense_id: Mapped[int] = mapped_column(ForeignKey("source_senses.id", ondelete="CASCADE"), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=utc_now, nullable=False)
