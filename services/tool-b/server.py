from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/secret")
def secret():
    return {"secret": "not-yet-protected"}
