from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime

from app.database.database import Base


class Review(Base):

    __tablename__ = "reviews"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    user_id = Column(
        Integer,
        nullable=False
    )


    repo_url = Column(
        String,
        nullable=False
    )


    issues = Column(
        JSON,
        nullable=False
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )