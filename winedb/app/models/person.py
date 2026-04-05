from typing import Optional, List
from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Person(Base):
    __tablename__ = "person"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)
    birth_year: Mapped[Optional[int]] = mapped_column(Integer)
    nationality: Mapped[Optional[str]] = mapped_column(Text)
    biography: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    winery_staff: Mapped[List["WineryStaff"]] = relationship(  # noqa: F821
        "WineryStaff", back_populates="person"
    )
    vineyard_ownerships: Mapped[List["VineyardOwner"]] = relationship(  # noqa: F821
        "VineyardOwner", back_populates="person"
    )
