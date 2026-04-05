from typing import Optional, List
from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class GrapeVariety(Base):
    __tablename__ = "grape_variety"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name_synonyms: Mapped[Optional[str]] = mapped_column(Text)
    color: Mapped[Optional[str]] = mapped_column(Text)  # "red" or "white"
    origin_region: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    wines: Mapped[List["Wine"]] = relationship(  # noqa: F821
        "Wine", back_populates="primary_variety"
    )
    wine_varieties: Mapped[List["WineGrapeVariety"]] = relationship(  # noqa: F821
        "WineGrapeVariety", back_populates="grape_variety"
    )
