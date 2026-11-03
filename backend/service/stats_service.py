from sqlalchemy.orm import Session
from sqlalchemy import func, select
from backend.models.user_word import UserWord
from backend.models.activity import DailyActivity
from datetime import date, timedelta
from backend.utils.activity_streak import get_streak_list
class Stats:
    def __init__(self,db:Session):
        self.db = db
    
    def all_words_in_vocablury_count(self,user_id: int):
        word_count = self.db.scalar(select(func.count(UserWord.id)).where(UserWord.user_id==user_id, UserWord.is_active==True))

        return {"Words in vocablury": word_count}
    
    def record_review(self, user_id:int):
        today = date.today()

        activity = self.db.scalar(select(DailyActivity).where(DailyActivity.user_id==user_id, DailyActivity.activity_date==today))
        if activity is None:
            activity = DailyActivity(user_id = user_id,
                                     activity_date = today,
                                     reviewed_cards = 1)
            self.db.add(activity)
        else:
            activity.reviewed_cards+=1
    
    def get_current_streak(self, user_id:int):
        activity_dates = self.db.scalars(select(DailyActivity.activity_date).where(DailyActivity.user_id==user_id).order_by(DailyActivity.activity_date.asc())).all()

        today = date.today()
        yesterday = today - timedelta(days=1)
        
        if not activity_dates:
            return 0
        
        if activity_dates[-1] not in (today,yesterday):
            return 0 
        
    
        streaks = get_streak_list(activity_dates)

        return streaks[-1]
    
    def get_max_streak(self, user_id:int):
        activity_dates = self.db.scalars(select(DailyActivity.activity_date).where(DailyActivity.user_id==user_id).order_by(DailyActivity.activity_date.asc())).all()

        if not activity_dates:
            return 0
        
        streaks = get_streak_list(activity_dates)

        return max(streaks)

