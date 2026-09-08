
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.review import Review
from app.services.github_service import get_repository_files
from app.services.ai_reviewer import review_code


router = APIRouter(
    prefix="/review",
    tags=["Review"]
)


class ReviewRequest(BaseModel):
    repo_url: str


@router.post("/")
def review_repository(
    request: ReviewRequest,
    db: Session = Depends(get_db)
):
    """
    Review a GitHub repository using Qwen
    and save the results in PostgreSQL.
    """

    try:

        # Get repository files from GitHub
        files = get_repository_files(
            request.repo_url
        )

        if not files:
            raise HTTPException(
                status_code=404,
                detail="No reviewable files found in repository"
            )

        print(
            f"Found {len(files)} files in repository"
        )

        # Send files to AI reviewer
        result = review_code(files)

        issues = result.get(
            "issues",
            []
        )

        # Save review in database
        review = Review(
            user_id=1,
            repo_url=request.repo_url,
            issues=issues
        )

        db.add(review)
        db.commit()
        db.refresh(review)

        return {
            "id": review.id,
            "repository": request.repo_url,
            "issues": issues
        }

    except HTTPException:
        raise

    except Exception as error:

        print(
            f"Review failed: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Repository review failed"
        )


@router.get("/{user_id}")
def get_reviews(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all reviews belonging to a user.
    """

    reviews = (
        db.query(Review)
        .filter(
            Review.user_id == user_id
        )
        .order_by(
            Review.created_at.desc()
        )
        .all()
    )

    return reviews
