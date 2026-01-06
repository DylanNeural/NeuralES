from fastapi import FastAPI

app = FastAPI(
    title="NeuralES API",
    version="0.1.0",
)

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
