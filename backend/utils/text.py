import string
import unicodedata


STRESS_MARKS = {"\u0300", "\u0301"}

RUSSIAN_LETTERS = set(
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
)

ENGLISH_LETTERS = set(
    string.ascii_lowercase
)

ALLOWED_SEPARATORS = {" ", "-", "'", "’"}


def normalize_dictionary_text(value: str) -> str:
    decomposed_text = unicodedata.normalize("NFD", value)

    text_without_stress = "".join(
        character
        for character in decomposed_text
        if character not in STRESS_MARKS
    )

    normalized_text = unicodedata.normalize(
        "NFC",
        text_without_stress,
    )

    return " ".join(
        normalized_text.casefold().split()
    )


def detect_dictionary_language(value: str) -> str:
    has_russian = False
    has_english = False

    for character in value:
        if character in ALLOWED_SEPARATORS:
            continue

        if character in RUSSIAN_LETTERS:
            has_russian = True

        elif character in ENGLISH_LETTERS:
            has_english = True

        else:
            raise ValueError(
                "Use only Russian or English letters"
            )

    if has_russian and has_english:
        return "mix"

    if has_russian:
        return "ru"

    if has_english:
        return "en"

    raise ValueError("Enter a word")