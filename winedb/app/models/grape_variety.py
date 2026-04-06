from typing import Optional, List
from sqlalchemy import Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class GrapeVariety(Base):
    __tablename__ = "grape_variety"
    __table_args__ = (UniqueConstraint("key", name="uq_grape_variety_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(Text, nullable=False)
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
    vineyard_grape_varieties: Mapped[List["VineyardGrapeVariety"]] = relationship(  # noqa: F821
        "VineyardGrapeVariety", back_populates="grape_variety"
    )
