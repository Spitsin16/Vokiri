from fastapi import FastAPI
from backend.routers import dictionary, auth

app = FastAPI(title="Vokiri API")

@app.get("/health")
def health():
    return {"status":"ok"}

app.include_router(dictionary.router)
app.include_router(auth.router)