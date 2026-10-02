from backend.models.dictionary import Lexeme, SourceSense, Translation, Definition, Pronunciation
from sqlalchemy import select

class DictionaryService:
    def __init__(self,db):
        self.db = db

    def lookup_word(self, word: str):
        normalized_word = word.strip().casefold()
        meanings=[]
        lexeme = self.db.scalar(select(Lexeme).where(Lexeme.normalized_lemma==normalized_word).limit(1))

        if not lexeme:
            raise ValueError("Word not found")
        
        senses = self.db.scalars(select(SourceSense).where(SourceSense.lexeme_id==lexeme.id).order_by(SourceSense.source_order)).all()
        
        for sense in senses:
            trans = self.db.scalars(select(Translation).where(Translation.sense_id==sense.id).order_by(Translation.source_order)).all()
            translations = []
            for tran in trans:
                translations.append(tran.text)
            definits = self.db.scalars(select(Definition).where(Definition.sense_id==sense.id).order_by(Definition.source_order)).all()
            definitions =[ ]
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
    
    def search(self, q):
        normalized_q = q.strip().casefold()

        if len(normalized_q) < 2:
            raise ValueError("Enter at least 2 characters")
    
        statement = (select(Lexeme.lemma).where(Lexeme.normalized_lemma.startswith(normalized_q,autoescape=True)).distinct().order_by(Lexeme.lemma).limit(5))

        words = self.db.scalars(statement).all()

        return {"query": q,
        "results": words}


        
