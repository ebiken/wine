from typing import Optional, List
from sqlalchemy import Integer, Text, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Wine(Base):
    __tablename__ = "wine"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    winery_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("winery.id"), nullable=False
    )
    label_name: Mapped[str] = mapped_column(Text, nullable=False)
    vintage_year: Mapped[int] = mapped_column(Integer, nullable=False)
    grape_variety_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("grape_variety.id"), nullable=True
    )
    ava_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("ava.id"), nullable=True
    )
    alcohol_pct: Mapped[Optional[float]] = mapped_column(Float)
    production_cases: Mapped[Optional[int]] = mapped_column(Integer)
    release_date: Mapped[Optional[Date]] = mapped_column(Date)
    tasting_notes: Mapped[Optional[str]] = mapped_column(Text)
    winery_description: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    winery: Mapped["Winery"] = relationship("Winery", back_populates="wines")  # noqa: F821
    primary_variety: Mapped[Optional["GrapeVariety"]] = relationship(  # noqa: F821
        "GrapeVariety", back_populates="wines"
    )
    ava: Mapped[Optional["AVA"]] = relationship("AVA", back_populates="wines")  # noqa: F821
    vineyard_sources: Mapped[List["WineVineyardSource"]] = relationship(  # noqa: F821
        "WineVineyardSource", back_populates="wine"
    )
    grape_varieties: Mapped[List["WineGrapeVariety"]] = relationship(  # noqa: F821
        "WineGrapeVariety", back_populates="wine"
    )
