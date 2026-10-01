from backend.database import Base
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(String(320),
                                       nullable=False,
                                       unique=True,
                                       index=True)
    
    password_hash: Mapped[str] = mapped_column(String(255),
                                               nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean,
                                            default=True,
                                            nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=utc_now,
                                                 nullable=False)