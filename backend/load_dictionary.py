import hashlib
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Base, engine
from backend.import_freedict import DATASET_PATH, iter_entries, DictionaryEntry
from backend.models import Definition, DictionarySource, Lexeme, Pronunciation, SourceSense,Translation

SOURCE_NAME = "FreeDict English-Russian"
SOURCE_VERSION = "2025.11.23"
LICENSE_NAME = "CC BY-SA 3.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/3.0/legalcode"
SOURCE_URL = "https://freedict.org/"

def calculate_file_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()

def get_or_create_dictionary_source(
    session: Session,
    dataset_path: Path,
) -> DictionarySource:
    file_hash = calculate_file_sha256(dataset_path)

    existing_source = session.scalar(
        select(DictionarySource).where(
            DictionarySource.name == SOURCE_NAME,
            DictionarySource.version == SOURCE_VERSION,
        )
    )

    if existing_source is not None:
        if existing_source.content_sha256 != file_hash:
            raise ValueError(
                "FreeDict file changed without a version change"
            )

        return existing_source

    source = DictionarySource(
        name=SOURCE_NAME,
        version=SOURCE_VERSION,
        license_name=LICENSE_NAME,
        license_url=LICENSE_URL,
        source_url=SOURCE_URL,
        content_sha256=file_hash,
    )

    session.add(source)
    session.flush()

    return source

def create_lexeme(session: Session,source: DictionarySource,entry: DictionaryEntry) -> Lexeme:
    lexeme = Lexeme(
        source_id=source.id,
        lemma=entry.lemma,
        normalized_lemma=entry.lemma.casefold(),
        part_of_speech=entry.part_of_speech or "unknown",
    )

    session.add(lexeme)
    session.flush()


    return lexeme

def create_pronunciations(session: Session,lexeme: Lexeme,entry: DictionaryEntry) -> None:
    for source_order, text in enumerate(entry.pronunciations,start=1):
        pronunciation = Pronunciation(lexeme_id=lexeme.id,
                                      text=text,
                                      source_order=source_order)

        session.add(pronunciation)

def create_source_sense(session: Session, lexeme: Lexeme, source_order: int):
    sense = SourceSense(lexeme_id=lexeme.id,
                        source_order=source_order,
                        verification_status="imported")
    
    session.add(sense)
    session.flush()
    return sense

def create_translations(session: Session, sense: SourceSense, translations: tuple[str, ...]):
    for source_order, text in enumerate(translations, start=1):
        translation = Translation(sense_id=sense.id,
                                  language="ru",
                                  source_order=source_order,
                                  text=text,
                                  normalized_text=" ".join(text.casefold().split()),
                                  verification_status="imported")

        session.add(translation)

def create_definitions(
    session: Session,
    sense: SourceSense,
    definitions: tuple[str, ...],
):
    for source_order, text in enumerate(definitions, start=1):
        text_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()

        definition = Definition(
            sense_id=sense.id,
            language="en",
            source_order=source_order,
            text=text,
            text_sha256=text_sha256,
            verification_status="imported",
        )

        session.add(definition)

def create_dictionary_entry(
    session: Session,
    source: DictionarySource,
    entry: DictionaryEntry,
):
    lexeme = create_lexeme(session, source, entry)
    create_pronunciations(session, lexeme, entry)

    for source_order, dictionary_sense in enumerate(
        entry.senses,
        start=1,
    ):
        sense = create_source_sense(
            session,
            lexeme,
            source_order,
        )

        create_translations(
            session,
            sense,
            dictionary_sense.translations,
        )

        create_definitions(
            session,
            sense,
            dictionary_sense.definitions,
        )

    return lexeme

def load_dictionary(dataset_path: Path = DATASET_PATH):
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        source = get_or_create_dictionary_source(
            session,
            dataset_path,
        )

        existing_lexeme_id = session.scalar(
            select(Lexeme.id)
            .where(Lexeme.source_id == source.id)
            .limit(1)
        )

        if existing_lexeme_id is not None:
            print("Dictionary is already loaded")
            return

        imported_count = 0

        for imported_count, entry in enumerate(
            iter_entries(dataset_path),
            start=1,
        ):
            create_dictionary_entry(
                session,
                source,
                entry,
            )

            if imported_count % 5000 == 0:
                print(f"Prepared {imported_count} words")

        session.commit()
        print(f"Imported {imported_count} words")


if __name__ == "__main__":
    load_dictionary()