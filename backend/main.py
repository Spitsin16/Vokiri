from fastapi import FastAPI

from backend.exceptions.exception_handlers import register_exception_handlers
from backend.routers import dictionary, auth, user_words, review, text_generation, user_texts

app = FastAPI(title="Vokiri API")

register_exception_handlers(app)

@app.get("/health")
def health():
    return {"status":"ok"}

app.include_router(dictionary.router)
app.include_router(auth.router)
app.include_router(user_words.router)
app.include_router(review.router)
app.include_router(text_generation.router)
app.include_router(user_texts.router)
