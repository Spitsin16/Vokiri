import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterator
import xml.etree.ElementTree as ET


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "data" / "raw" / "eng-rus.tei"

TEI_NAMESPACE = "{http://www.tei-c.org/ns/1.0}"

TEST_WORDS = {
    "bank",
    "bound",
    "increase",
    "reduce",
    "reluctant",
}


@dataclass(frozen=True)
class DictionarySense:
    translations: tuple[str, ...]
    definitions: tuple[str, ...]


@dataclass(frozen=True)
class DictionaryEntry:
    lemma: str
    part_of_speech: str | None
    pronunciations: tuple[str, ...]
    senses: tuple[DictionarySense, ...]


def normalize_text(value: str | None) -> str:
    return " ".join((value or "").split())


def element_text(element: ET.Element) -> str:
    return normalize_text("".join(element.itertext()))


def parse_entry(element: ET.Element) -> DictionaryEntry | None:
    lemma = normalize_text(
        element.findtext(f"./{TEI_NAMESPACE}form/{TEI_NAMESPACE}orth")
    )
    if not lemma:
        return None

    part_of_speech = normalize_text(
        element.findtext(f"./{TEI_NAMESPACE}gramGrp/{TEI_NAMESPACE}pos")
    ) or None
    pronunciations = tuple(
        text
        for node in element.findall(f"./{TEI_NAMESPACE}form/{TEI_NAMESPACE}pron")
        if (text := element_text(node))
    )

    senses: list[DictionarySense] = []
    for sense in element.findall(f"./{TEI_NAMESPACE}sense"):
        translations = tuple(
            text
            for node in sense.findall(
                f"./{TEI_NAMESPACE}cit[@type='trans']/{TEI_NAMESPACE}quote"
            )
            if (text := element_text(node))
        )
        definitions = tuple(
            text
            for node in sense.findall(f".//{TEI_NAMESPACE}def")
            if (text := element_text(node))
        )
        if translations or definitions:
            senses.append(DictionarySense(translations, definitions))

    if not senses:
        return None

    return DictionaryEntry(
        lemma=lemma,
        part_of_speech=part_of_speech,
        pronunciations=pronunciations,
        senses=tuple(senses),
    )


def iter_entries(
    dataset_path: Path,
    wanted_words: set[str] | None = None,
) -> Iterator[DictionaryEntry]:
    wanted = (
        {word.casefold() for word in wanted_words}
        if wanted_words is not None
        else None
    )

    for _, element in ET.iterparse(dataset_path, events=("end",)):
        if element.tag != f"{TEI_NAMESPACE}entry":
            continue

        parsed = parse_entry(element)
        element.clear()

        if parsed is None:
            continue
        if wanted is not None and parsed.lemma.casefold() not in wanted:
            continue
        yield parsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect FreeDict English-Russian data")
    parser.add_argument("words", nargs="*", help="English words to inspect")
    arguments = parser.parse_args()
    words = set(arguments.words) or TEST_WORDS

    for entry in iter_entries(DATASET_PATH, words):
        print(json.dumps(asdict(entry), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
