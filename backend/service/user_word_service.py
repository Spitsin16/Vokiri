from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.models.dictionary import SourceSense, Lexeme, Translation
from backend.models.user_word import UserWord

class UserWordService:
    def __init__(self, db: Session):
        self.db = db
    
    def add_word(self, user_id: int, sense_id: int):

        sense = self.db.scalar(select(SourceSense).where(SourceSense.id == sense_id))

        if sense is None:
            raise LookupError("Meaning not found")
        
        sense_in_user_word = self.db.scalar(select(UserWord).where(UserWord.source_sense_id == sense_id,UserWord.user_id == user_id))

        if sense_in_user_word is not None:
            raise ValueError("Meaning already in dictionary")
        
        user_word = UserWord(user_id = user_id, source_sense_id = sense_id )

        self.db.add(user_word)
        self.db.commit()
        self.db.refresh(user_word)

        return user_word
    
    def get_all_words(self, user_id: int):
        words = self.db.scalars(select(UserWord).where(UserWord.user_id == user_id)).all()
        result = []
        for word in words:
            sense = self.db.scalar(select(SourceSense).where(SourceSense.id == word.source_sense_id))
            lexeme = self.db.scalar(select(Lexeme).where(Lexeme.id == sense.lexeme_id))
            translations = self.db.scalars(select(Translation.text).where(Translation.sense_id == sense.id).order_by(Translation.source_order)).all()

            result.append(
            {
                "id": word.id,
                "sense_id": sense.id,
                "word": lexeme.lemma,
                "translation": translations,
                "is_active": word.is_active,
                "created_at": word.created_at,
            }
        )
        return result