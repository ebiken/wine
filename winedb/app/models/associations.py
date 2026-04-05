from typing import Optional
from sqlalchemy import Integer, Text, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class WineryStaff(Base):
    __tablename__ = "winery_staff"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    winery_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("winery.id"), nullable=False
    )
    person_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("person.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(Text, nullable=False)
    year_start: Mapped[Optional[int]] = mapped_column(Integer)
    year_end: Mapped[Optional[int]] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    winery: Mapped["Winery"] = relationship("Winery", back_populates="staff")  # noqa: F821
    person: Mapped["Person"] = relationship("Person", back_populates="winery_staff")  # noqa: F821


class WineVineyardSource(Base):
    __tablename__ = "wine_vineyard_source"
    __table_args__ = (
        UniqueConstraint("wine_id", "vineyard_id", "block_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("wine.id"), nullable=False
    )
    vineyard_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vineyard.id"), nullable=False
    )
    block_name: Mapped[Optional[str]] = mapped_column(Text)
    pct_blend: Mapped[Optional[float]] = mapped_column(Float)

    wine: Mapped["Wine"] = relationship("Wine", back_populates="vineyard_sources")  # noqa: F821
    vineyard: Mapped["Vineyard"] = relationship("Vineyard", back_populates="wine_sources")  # noqa: F821


class WineGrapeVariety(Base):
    __tablename__ = "wine_grape_variety"
    __table_args__ = (
        UniqueConstraint("wine_id", "grape_variety_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("wine.id"), nullable=False
    )
    grape_variety_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("grape_variety.id"), nullable=False
    )
    pct_blend: Mapped[Optional[float]] = mapped_column(Float)

    wine: Mapped["Wine"] = relationship("Wine", back_populates="grape_varieties")  # noqa: F821
    grape_variety: Mapped["GrapeVariety"] = relationship(  # noqa: F821
        "GrapeVariety", back_populates="wine_varieties"
    )


class VineyardOwner(Base):
    __tablename__ = "vineyard_owner"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vineyard_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vineyard.id"), nullable=False
    )
    person_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("person.id"), nullable=False
    )
    ownership_role: Mapped[Optional[str]] = mapped_column(Text)
    year_start: Mapped[Optional[int]] = mapped_column(Integer)
    year_end: Mapped[Optional[int]] = mapped_column(Integer)

    vineyard: Mapped["Vineyard"] = relationship("Vineyard", back_populates="owners")  # noqa: F821
    person: Mapped["Person"] = relationship(  # noqa: F821
        "Person", back_populates="vineyard_ownerships"
    )
