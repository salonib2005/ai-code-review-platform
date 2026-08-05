from fastapi import FastAPI

from app.api import auth

from app.database.database import engine, Base

from app.models import user


Base.metadata.create_all(
    bind=engine
)


app = FastAPI()


app.include_router(
    auth.router,
    prefix="/auth"
)


@app.get("/")
def root():

    return {
        "message": "AI Code Review Platform Backend 🚀"
    }