from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.repository import Repository


router = APIRouter()


@router.get("/{user_id}")
def get_repositories(
    user_id: int,
    db: Session = Depends(get_db)
):

    repos = db.query(Repository).filter(
        Repository.user_id == user_id
    ).all()


    return [
        {
            "id": repo.id,
            "name": repo.name,
            "url": repo.url,
            "language": repo.language
        }
        for repo in repos
    ]