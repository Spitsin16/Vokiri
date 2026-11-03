import pytest
from pydantic import ValidationError

from backend.service.ai_integration import parse_generated_text


def test_parse_generated_text_accepts_json():
    result = parse_generated_text(
        '{"title": "Learning", "text": "A short English text."}'
    )

    assert result.title == "Learning"
    assert result.text == "A short English text."


def test_parse_generated_text_accepts_json_code_fence():
    result = parse_generated_text(
        '```json\n{"title": "Learning", "text": "A short English text."}\n```'
    )

    assert result.title == "Learning"
    assert result.text == "A short English text."


def test_parse_generated_text_rejects_invalid_response():
    with pytest.raises(ValidationError):
        parse_generated_text("This is not JSON")
