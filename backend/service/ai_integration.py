import os
import json

from backend.config import GIGACHAT_CREDENTIALS, GIGACHAT_VERSION
from gigachat import GigaChat
from gigachat.exceptions import GigaChatException

class AiIntegration:
    def __init__(self,db):
        self.db = db
    
    def generate_text(self, level:str, min_words: int, max_words:int, theme: str):

        prompt = f"""
You are the reading-text generator for Vokiri, an English-learning application.

Create one coherent and original English reading text.

Parameters:
- CEFR level: {level}
- Topic: {theme}
- Required length: from {min_words} to {max_words} words

Requirements:

1. Match the requested CEFR level in grammar, vocabulary, and sentence structure.
2. Keep the entire text focused on the requested topic.
3. Write an engaging story or realistic situation, not a list of unrelated facts.
4. Stay between {min_words} and {max_words} words.
5. Give the text a short English title.
6. Divide the text into natural paragraphs when appropriate.
7. Do not include translations, exercises, explanations, vocabulary lists, or comments about the task.
8. Do not use Markdown.
9. If the topic mentions a real person, university, company, or event, do not invent specific facts, dates, statistics, or quotations.

Return only valid JSON in exactly this format:

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