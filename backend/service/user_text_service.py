from sqlalchemy import select
from backend.models.text import UserText, AllText
from backend.exceptions.exceptions_classes  import NotFoundError
class UserTextService:
    def __init__(self, db):
        self.db = db
    
    def get_all_texts(self, user_id: int):
        all_user_texts = self.db.scalars(select(UserText).where(user_id==UserText.user_id)).all()
        text_list=[]
        for text in all_user_texts:
            find_text = self.db.scalar(select(AllText).where(text.text_id==AllText.id))
            text_list.append({"title" : find_text.title,
                              "id": find_text.id})
        return text_list
    
    def get_certain_text(self,text_id: int , user_id: int):
        user_text = self.db.scalar(select(UserText).where(UserText.text_id==text_id,UserText.user_id==user_id))
        if not user_text:
            raise NotFoundError("Wrong text id")
        
        text = self.db.scalar(select(AllText).where(user_text.text_id==AllText.id))
        
        return {"title": text.title,
                "content": text.content}


