from fastapi import FastAPI
from app.api import auth

app = FastAPI()

app.include_router(
    auth.router,
    prefix="/auth"
)


@app.get("/")
def root():
    return {
        "status":"running",
        "message":"AI Code Review Platform Backend 🚀"
    }