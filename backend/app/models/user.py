from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class User(Base):

    __tablename__ = "users"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    github_id = Column(
        String,
        unique=True
    )

    username = Column(String)

    name = Column(String)

    avatar = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    repositories = relationship(
        "Repository",
        back_populates="user"
    )