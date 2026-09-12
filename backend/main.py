from fastapi import FastAPI, Depends,HTTPException, Query

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Lexeme, SourceSense, Translation, Pronunciation, Definition

app = FastAPI(title="Vokiri API")

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/dictionary/lookup")
def lookup_word(word: str, db: Session=Depends(get_db)):
    normalized_word = word.strip().casefold()
    meanings=[]
    
    lexeme = db.scalar(select(Lexeme).where(Lexeme.normalized_lemma==normalized_word).limit(1))

    if not lexeme:
        raise HTTPException(status_code=404, detail="Word not found")
    
    senses = db.scalars(select(SourceSense).where(SourceSense.lexeme_id==lexeme.id).order_by(SourceSense.source_order)).all()
    
    for sense in senses:
        trans=db.scalars(select(Translation).where(Translation.sense_id==sense.id).order_by(Translation.source_order)).all()
        translations=[]
        for tran in trans:
            translations.append(tran.text)
        definits=db.scalars(select(Definition).where(Definition.sense_id==sense.id).order_by(Definition.source_order)).all()
        definitions=[]
        for definit in definits:
            definitions.append(definit.text)

        meanings.append({"sense_id": sense.id,
                         "order": sense.source_order,
                         "translations": translations,
                         "definitions": definitions})
    pronunciations = db.scalars(select(Pronunciation.text).where(Pronunciation.lexeme_id == lexeme.id).order_by(Pronunciation.source_order)).all()

    return {"id": lexeme.id,
            "word": lexeme.lemma,
            "part_of_speech": lexeme.part_of_speech,
            "pronunciations": pronunciations,
            "meanings": meanings}

@app.get("/dictionary/search")
def search(q: str = Query(min_length=2), db: Session=Depends(get_db)):
    normalized_q = q.strip().casefold()

    if len(normalized_q) < 2:
        raise HTTPException(status_code=404,detail="Enter at least 2 characters")
    
    statement = (select(Lexeme.lemma).where(Lexeme.normalized_lemma.startswith(normalized_q,autoescape=True)).distinct().order_by(Lexeme.lemma).limit(5))

    words = db.scalars(statement).all()

    return {"query": q,
    "results": words}
