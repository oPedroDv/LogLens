from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(title="LogLens")
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "LogLens is running"}