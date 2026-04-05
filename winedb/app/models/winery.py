from typing import Optional, List
from sqlalchemy import Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Winery(Base):
    __tablename__ = "winery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    established_year: Mapped[Optional[int]] = mapped_column(Integer)
    location_city: Mapped[Optional[str]] = mapped_column(Text)
    location_state: Mapped[Optional[str]] = mapped_column(Text)
    ava_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("ava.id"), nullable=True
    )
    is_negociant: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    website: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    ava: Mapped[Optional["AVA"]] = relationship("AVA", back_populates="wineries")  # noqa: F821
    staff: Mapped[List["WineryStaff"]] = relationship(  # noqa: F821
        "WineryStaff", back_populates="winery"
    )
    wines: Mapped[List["Wine"]] = relationship("Wine", back_populates="winery")  # noqa: F821
