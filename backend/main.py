from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import engine, Base

from app.models import User, Repository, Review

from app.api import auth
from app.api import repositories
from app.api import users
from app.api import review
from app.api import history


app = FastAPI()


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    review.router,
    prefix="/review"
)

app.include_router(
    history.router,
    prefix="/history"
)

app.include_router(
    auth.router,
    prefix="/auth"
)


app.include_router(
    repositories.router,
    prefix="/repositories"
)


app.include_router(
    users.router,
    prefix="/users"
)


@app.get("/")
def root():
    return {
        "message": "AI Code Review Platform Backend 🚀"
    }