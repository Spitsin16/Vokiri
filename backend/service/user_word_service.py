from sqlalchemy.orm import Session
from sqlalchemy import select,or_
from backend.exceptions.exceptions_classes import ConflictError, NotFoundError, ValidationError
from backend.models.dictionary import SourceSense, Lexeme, Translation
from backend.models.user_word import UserWord
from datetime import date, timedelta

class UserWordService:
    def __init__(self, db: Session):
        self.db = db

    def add_word(self,user_id: int,sense_id: int,translation_id: int | None,custom_translation: str | None):

        if translation_id is None and custom_translation is None:
            raise ValidationError("Choose a translation")

        if translation_id is not None and custom_translation is not None:
            raise ValidationError("Choose only one translation")

        sense = self.db.scalar(select(SourceSense).where(SourceSense.id == sense_id))

        if sense is None:
            raise NotFoundError("Meaning not found")

        if translation_id is not None:
            translation = self.db.scalar(select(Translation).where(Translation.id == translation_id,Translation.sense_id == sense_id))

            if translation is None:
                raise ValidationError("Translation does not belong to this meaning")

        if custom_translation is not None:
            custom_translation = custom_translation.strip()

            if not custom_translation:
                raise ValidationError("Custom translation cannot be empty")

        user_word = self.db.scalar(select(UserWord).where(UserWord.source_sense_id == sense_id,UserWord.user_id == user_id))

        if user_word is not None:
            if user_word.is_active is True:
                raise ConflictError(
                    "Meaning already in dictionary"
                )

            user_word.is_active = True
            user_word.preferred_translation_id = translation_id
            user_word.custom_translation = custom_translation

        else:
            user_word = UserWord(
                user_id=user_id,
                source_sense_id=sense_id,
                preferred_translation_id=translation_id,
                custom_translation=custom_translation,
            )

            self.db.add(user_word)

        self.db.commit()
        self.db.refresh(user_word)

        return user_word




    def get_all_words(self, user_id: int):
        words = self.db.scalars(select(UserWord).where(UserWord.user_id == user_id)).all()
        result = []
        for word in words:
            if word.is_active == True:
                sense = self.db.scalar(select(SourceSense).where(SourceSense.id == word.source_sense_id))
                lexeme = self.db.scalar(select(Lexeme).where(Lexeme.id == sense.lexeme_id))
                if word.custom_translation is None:
                    translation = self.db.scalar(select(Translation.text).where(Translation.sense_id == sense.id,Translation.id == word.preferred_translation_id))
                else:
                    translation = word.custom_translation

                result.append(
                {
                    "id": word.id,
                    "sense_id": sense.id,
                    "word": lexeme.lemma,
                    "translation": translation,
                    "is_active": word.is_active,
                    "created_at": word.created_at,
                }
            )
        return result

    def delete_word(self, user_id: int, sense_id: int):
        word = self.db.scalar(select(UserWord).where(UserWord.source_sense_id == sense_id,UserWord.user_id == user_id))

        if (word is None) or (word.is_active is False):
            raise NotFoundError("Meaning not found in your dictionary")


        word.is_active = False

        self.db.commit()
        self.db.refresh(word)

        return word

    def get_today_cards(self, user_id: int, limit: int):
        words = self.db.scalars(select(UserWord).where(UserWord.user_id == user_id,UserWord.is_active == True,or_(UserWord.next_review_date.is_(None),UserWord.next_review_date <= date.today(),),).limit(limit)).all()

        eligible_ids = [word.id for word in words]
        all_words = self.get_all_words(user_id)

        return [word for word in all_words if word["id"] in eligible_ids]

    def answer_card(self, user_id: int, user_word_id: int, answer: str):

        view_table = {0:0,
                      1:1,
                      2:2,
                      3:4,
                      4:7,
                      5:14,
                      6:30,
                      7:60}

        word = self.db.scalar(select(UserWord).where(UserWord.user_id==user_id, UserWord.id==user_word_id, UserWord.is_active==True))

        if word is None:
            raise NotFoundError("Word not found")

        if answer == "good":
            word.review_step+=1
            word.review_step = min(7,word.review_step)
        elif answer == "again":
            word.review_step-=2
            word.review_step = max(0,word.review_step)
            if word.review_step<0:
                word.review_step+=0
        elif answer == "hard":
            word.review_step+=0
        else:
            raise(ValidationError("Unknown review answer"))
        word.next_review_date = date.today() + timedelta(view_table[word.review_step])
        self.db.commit()
        self.db.refresh(word)


        return {"user_word_id": user_word_id,
                "answer": answer,
                "next_show": word.next_review_date}
