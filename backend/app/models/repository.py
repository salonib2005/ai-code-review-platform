from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Repository(Base):

    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    name = Column(String)
    url = Column(String)
    language = Column(String, nullable=True)


    user = relationship(
        "User",
        back_populates="repositories"
    )