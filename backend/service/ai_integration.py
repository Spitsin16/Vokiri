import json

from backend.config import GIGACHAT_CREDENTIALS, GIGACHAT_VERSION
from gigachat import GigaChat
from gigachat.exceptions import GigaChatException
from sqlalchemy import select, case, or_

from backend.service.user_word_service import UserWordService
from backend.models.text import AllText, UserText
from backend.utils.prompts import create_prompt

class AiIntegration:
    def __init__(self,db):
        self.db = db

    def generate_text(self, level:str, min_words: int, max_words:int, theme: str,user_id: int ):
        service = UserWordService(self.db)
        words = service.get_today_cards(user_id, 5)
        word_list=[]

        for word in words:
            word_list.append({"word":word["word"], "translation": word["translation"]})

        prompt = create_prompt(level,min_words, max_words, theme, word_list)
        try:
            with GigaChat(
                credentials=GIGACHAT_CREDENTIALS,
                scope="GIGACHAT_API_PERS",
                model=GIGACHAT_VERSION,
                timeout=60,
            ) as client:
                response = client.chat.create(prompt)

            raw_result = response.messages[0].content[0].text
            result = json.loads(raw_result)

        except GigaChatException as error:
            raise ValueError("Error GIGACHAT")

        new_text = AllText(title = result["title"],
                       theme = theme,
                       level = level,
                       target_words = word_list,
                       word_count = len(result["text"].split()),
                       content = result["text"])

        self.db.add(new_text)
        self.db.flush()

        user_text = UserText(user_id = user_id,
                             text_id = new_text.id)

        self.db.add(user_text)
        self.db.commit()
        self.db.refresh(new_text)

        return result
