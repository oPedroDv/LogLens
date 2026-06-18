from fastapi import FastAPI
from app.api.router import router

app = FastAPI(title="LogLens")
app.include_router(router)

@app.get("/")
def root():
    return {"message": "LogLens is running"}