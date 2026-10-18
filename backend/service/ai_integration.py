import os
import json

from backend.config import GIGACHAT_CREDENTIALS, GIGACHAT_VERSION
from gigachat import GigaChat
from gigachat.exceptions import GigaChatException
from sqlalchemy import select, case, or_
from datetime import date
from backend.models.user_word import UserWord
from backend.service.user_word_service import UserWordService
class AiIntegration:
    def __init__(self,db):
        self.db = db
    
    def generate_text(self, level:str, min_words: int, max_words:int, theme: str,user_id: int ):
        service = UserWordService(self.db)
        words = service.get_today_cards(user_id, 5)
        word_list=[]

        for word in words:
            word_list.append({"word":word["word"], "translation": word["translation"]})

        prompt = f"""
You are an educational writer for Vokiri, an English-learning application.

Create one coherent and engaging English reading text.

USER PARAMETERS:
- CEFR level: {level}
- Topic: {theme}
- Required length: {min_words}-{max_words} words

TARGET VOCABULARY:
{word_list}

VOCABULARY RULES:
1. Use every target English word naturally in the text.
2. Use each word with the meaning indicated by its Russian translation.
3. Do not place the words in an artificial list or unrelated sentences.
4. Make their meaning understandable from the surrounding context.
5. Preserve the exact spelling of every target word at least once.

CONTENT RULES:
1. Match the requested CEFR level in vocabulary, grammar, and sentence structure.
2. Keep the entire text focused on the requested topic.
3. Write a coherent article, biography, historical account, or realistic story.
4. Stay between {min_words} and {max_words} words.
5. Give the text a short English title.
6. Divide the text into natural paragraphs.
7. Do not include translations, exercises, vocabulary lists, Markdown, or comments about the task.
8. Do not invent quotations, dates, statistics, names, events, or biographical details.
9. If a factual detail is uncertain, omit it.

Return only valid JSON:

{{
  "title": "Short English title",
  "text": "Generated English text"
}}

Do not wrap the JSON in Markdown code fences.
"""

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
            return result

        except GigaChatException as error:
            raise ValueError("Error GIGACHAT")