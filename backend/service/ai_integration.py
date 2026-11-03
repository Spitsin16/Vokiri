from pathlib import Path

from backend.config import GIGACHAT_CREDENTIALS, GIGACHAT_VERSION
from backend.exceptions.exceptions_classes import AiServiceError
from backend.models.text import AllText, UserText
from backend.schemas.text import GeneratedText
from backend.service.user_word_service import UserWordService
from backend.utils.prompts import create_prompt
from gigachat import GigaChat
from gigachat.exceptions import GigaChatException
from httpx import HTTPError
from pydantic import ValidationError as PydanticValidationError
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from backend.exceptions.exceptions_classes import RateLimitError
from backend.config import AI_DAILY_GENERATION_LIMIT
GIGACHAT_CA_BUNDLE_FILE = (
    Path(__file__).resolve().parent.parent
    / "certs"
    / "russian_trusted_root_ca_pem.crt"
)


def parse_generated_text(raw_result: str) -> GeneratedText:
    cleaned_result = raw_result.strip()

    if cleaned_result.startswith("```") and cleaned_result.endswith("```"):
        opening_line_end = cleaned_result.find("\n")

        if opening_line_end != -1:
            cleaned_result = cleaned_result[opening_line_end + 1:-3].strip()

    return GeneratedText.model_validate_json(cleaned_result)


class AiIntegration:
    def __init__(self,db):
        self.db = db
    
    def check_generated_limit(self, user_id: int ):
        period_start = datetime.now(timezone.utc) - timedelta(hours=24)

        generation_count = self.db.scalar(
            select(func.count(UserText.id))
            .join(AllText, UserText.text_id == AllText.id)
            .where(
                UserText.user_id == user_id,
                AllText.created_at >= period_start,
            )
        )

        if generation_count >= AI_DAILY_GENERATION_LIMIT:
            raise RateLimitError("Too much generations. Daily limit=3")

    def generate_text(self, level:str, min_words: int, max_words:int, theme: str,user_id: int, limit_words: int):
        self.check_generated_limit(user_id)
        service = UserWordService(self.db)
        words = service.get_today_cards(user_id, limit_words)
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
                ca_bundle_file=str(GIGACHAT_CA_BUNDLE_FILE),
            ) as client:
                response = client.chat.create(prompt)

            raw_result = response.messages[0].content[0].text
            result = parse_generated_text(raw_result)

        except (GigaChatException, HTTPError) as error:
            raise AiServiceError(
                "AI service is unavailable"
            ) from error

        except PydanticValidationError as error:
            raise AiServiceError(
                "AI returned an invalid response"
            ) from error

        new_text = AllText(title = result.title,
                       theme = theme,
                       level = level,
                       target_words = word_list,
                       word_count = len(result.text.split()),
                       content = result.text)

        self.db.add(new_text)
        self.db.flush()

        user_text = UserText(user_id = user_id,
                             text_id = new_text.id)

        self.db.add(user_text)
        self.db.commit()
        self.db.refresh(new_text)

        return result
