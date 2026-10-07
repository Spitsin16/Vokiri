from backend.models.dictionary import Lexeme, SourceSense, Translation, Definition, Pronunciation
from sqlalchemy import select
from backend.utils.text import detect_dictionary_language, normalize_dictionary_text

class DictionaryService:
    def __init__(self,db):
        self.db = db

    def lookup_word(self, word: str):
        normalized_word = normalize_dictionary_text(word)
        meanings=[]
        word_language = detect_dictionary_language(normalized_word)
        if word_language == "en":
            lexeme = self.db.scalar(select(Lexeme).where(Lexeme.normalized_lemma==normalized_word).limit(1))

            if not lexeme:
                raise ValueError("Word not found")

            senses = self.db.scalars(select(SourceSense).where(SourceSense.lexeme_id==lexeme.id).order_by(SourceSense.source_order)).all()

            for sense in senses:
                trans = self.db.scalars(select(Translation).where(Translation.sense_id==sense.id).order_by(Translation.source_order)).all()
                translations = []
                for tran in trans:
                    translations.append({"text": tran.text,
                                        "id": tran.id})
                definits = self.db.scalars(select(Definition).where(Definition.sense_id==sense.id).order_by(Definition.source_order)).all()
                definitions =[]
                for definit in definits:
                    definitions.append(definit.text)

                meanings.append({"sense_id": sense.id,
                                "order": sense.source_order,
                                "translations": translations,
                                "definitions": definitions})

            pronunciations = self.db.scalars(select(Pronunciation.text).where(Pronunciation.lexeme_id == lexeme.id).order_by(Pronunciation.source_order)).all()

            return {"id": lexeme.id,
                    "word": lexeme.lemma,
                    "part_of_speech": lexeme.part_of_speech,
                    "pronunciations": pronunciations,
                    "meanings": meanings}
        
        elif word_language == "ru":
            statement = (
                select(Lexeme,SourceSense,Translation,).join(SourceSense,SourceSense.lexeme_id == Lexeme.id,).join(Translation,Translation.sense_id == SourceSense.id,).where(Translation.normalized_text == normalized_word).order_by(Lexeme.lemma).limit(10))

            matches = self.db.execute(statement).all()

            if not matches:
                raise ValueError("Word not found")

            results = []

            for lexeme, sense, translation in matches:
                results.append(
                    {
                        "lexeme_id": lexeme.id,
                        "word": lexeme.lemma,
                        "part_of_speech": lexeme.part_of_speech,
                        "sense_id": sense.id,
                        "translation": {
                            "id": translation.id,
                            "text": translation.text,
                        },
                    }
                )

            return {
                "query": word,
                "language": "ru",
                "results": results,
            }
        else:
            raise LookupError("Word must be written by single language")

    def search(self, q):
        normalized_q = normalize_dictionary_text(q)

        if len(normalized_q) < 2:
            raise ValueError("Enter at least 2 characters")

        word_language = detect_dictionary_language(normalized_q)

        if word_language == "en":
            statement = (select(Lexeme.lemma).where(Lexeme.normalized_lemma.startswith(normalized_q,autoescape=True)).distinct().order_by(Lexeme.lemma).limit(5))

            words = self.db.scalars(statement).all()

            return {"query": q,
            "results": words}
        
        elif word_language == "ru":
            statement = (select(Translation.normalized_text).where(Translation.normalized_text.startswith(normalized_q,autoescape=True)).distinct().order_by(Translation.normalized_text).limit(5))
            words = self.db.scalars(statement).all()

            return {"query": q,
                    "results": words}
        else:
            raise LookupError("Word must be written by single language")




        
