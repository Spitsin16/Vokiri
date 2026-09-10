from fastapi import FastAPI

app = FastAPI(title="Vokiri API")

@app.get("/health")
def health():
    return {"status":"ok"}
