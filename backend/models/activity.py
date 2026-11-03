from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base

class DailyActivity(Base):
    __tablename__ = "daily_activities"

    __table_args__ = (UniqueConstraint("user_id",
                                       "activity_date",
                                       name="uq_daily_activity_user_date",),)

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"),
                                         nullable=False)
    
    activity_date: Mapped[date] = mapped_column(Date,
                                                nullable=False)
    
    reviewed_cards: Mapped[int] = mapped_column(Integer,
                                                default=0,
                                                server_default=text("0"),
                                                nullable=False)
    