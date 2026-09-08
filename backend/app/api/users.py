from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User

router = APIRouter()


@router.get("/{username}")
def get_user(
    username: str,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user:
        return {
            "message": "User not found"
        }

    return {
        "id": user.id,
        "github_id": user.github_id,
        "username": user.username,
        "name": user.name,
        "avatar": user.avatar,
        "created_at": user.created_at
    }