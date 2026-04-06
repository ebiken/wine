from typing import Optional, List
from sqlalchemy import Integer, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Vineyard(Base):
    __tablename__ = "vineyard"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    ava_id: Mapped[int] = mapped_column(Integer, ForeignKey("ava.id"), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    elevation_ft_low: Mapped[Optional[int]] = mapped_column(Integer)
    elevation_ft_high: Mapped[Optional[int]] = mapped_column(Integer)
    total_acres: Mapped[Optional[int]] = mapped_column(Integer)
    soil_type: Mapped[Optional[str]] = mapped_column(Text)
    established_year: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    ava: Mapped["AVA"] = relationship("AVA", back_populates="vineyards")  # noqa: F821
    owners: Mapped[List["VineyardOwner"]] = relationship(  # noqa: F821
        "VineyardOwner", back_populates="vineyard"
    )
    wine_sources: Mapped[List["WineVineyardSource"]] = relationship(  # noqa: F821
        "WineVineyardSource", back_populates="vineyard"
    )
    vineyard_grape_varieties: Mapped[List["VineyardGrapeVariety"]] = relationship(  # noqa: F821
        "VineyardGrapeVariety",
        back_populates="vineyard",
        order_by="VineyardGrapeVariety.sort_order",
    )
