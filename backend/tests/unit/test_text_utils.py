from backend.utils.text import detect_dictionary_language, normalize_dictionary_text
from backend.utils.prompts import create_prompt
import pytest

@pytest.mark.parametrize(("word","expected_language"),[("hello", "en"), ("привет", "ru"), ("приhell","mix")])
def test_detect_language(word, expected_language):
    result = detect_dictionary_language(word)
    assert result == expected_language

@pytest.mark.parametrize(("word","expected_result"),[("HellO","hello"),("яче́йник","ячейник"),("ПРИВЕТ","привет"),("HELLO","hello"),("  Hello hello","hello hello")])
def test_normalize_dictionary_text(word, expected_result):
    result = normalize_dictionary_text(word)
    assert result == expected_result

def test_check_prompt():
    prompt = create_prompt("B1", 100, 150, "Football", [{"word": "achieve", "translation": "достигать"}])

    assert "B1" in prompt
    assert "100-150 words" in prompt
    assert "Football" in prompt
    assert "achieve" in prompt
    assert "достигать" in prompt
    assert '"title"' in prompt
    assert '"text"' in prompt