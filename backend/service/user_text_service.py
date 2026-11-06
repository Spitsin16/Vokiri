from sqlalchemy import select
from backend.models.text import UserText, AllText
from backend.exceptions.exceptions_classes  import NotFoundError
class UserTextService:
    def __init__(self, db):
        self.db = db
    
    def get_all_texts(self, user_id: int):
        texts = self.db.execute(
            select(AllText.id, AllText.title)
            .join(UserText, UserText.text_id == AllText.id)
            .where(UserText.user_id == user_id,UserText.is_active.is_(True))
        ).all()

        return [{"title": title, "id": text_id} for text_id, title in texts]
    
    def get_certain_text(self,text_id: int , user_id: int):
        text = self.db.scalar(
            select(AllText)
            .join(UserText, UserText.text_id == AllText.id)
            .where(
                UserText.text_id == text_id,
                UserText.user_id == user_id,
                UserText.is_active.is_(True)
            )
        )
        if not text:
            raise NotFoundError("Wrong text id")
        
        return {"title": text.title,
                "content": text.content}

    def delete_text(self, user_id: int, text_id: int):
        text = self.db.scalar(
            select(UserText)
            .where(
                UserText.text_id == text_id,
                UserText.user_id == user_id,
                UserText.is_active.is_(True)
            )
        )

        if not text:
            raise NotFoundError("Wrong text id")

        text.is_active = False

        self.db.commit()
        self.db.refresh(text)

        return text
