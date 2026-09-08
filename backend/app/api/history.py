from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.review import Review


router = APIRouter()



# Get review history of a user

@router.get("/{user_id}")
def get_review_history(
    user_id: int,
    db: Session = Depends(get_db)
):

    reviews = (
        db.query(Review)
        .filter(Review.user_id == user_id)
        .order_by(Review.created_at.desc())
        .all()
    )


    result = []


    for review in reviews:

        warnings = 0
        suggestions = 0


        for issue in review.issues:

            if issue["severity"] == "warning":
                warnings += 1

            elif issue["severity"] == "suggestion":
                suggestions += 1



        result.append(
            {
                "id": review.id,

                "repo_url": review.repo_url,

                "issues_count": len(review.issues),

                "warnings": warnings,

                "suggestions": suggestions,

                "created_at": review.created_at
            }
        )


    return result




# Get complete details of one review

@router.get("/review/{review_id}")
def get_single_review(
    review_id: int,
    db: Session = Depends(get_db)
):

    review = (
        db.query(Review)
        .filter(Review.id == review_id)
        .first()
    )


    if not review:

        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )


    return {
        "id": review.id,
        "repo_url": review.repo_url,
        "issues": review.issues,
        "created_at": review.created_at
    }