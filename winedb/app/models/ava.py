from typing import Optional, List
from sqlalchemy import Integer, Text, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AVA(Base):
    __tablename__ = "ava"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column(Text)
    parent_ava_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("ava.id"), nullable=True
    )
    state: Mapped[str] = mapped_column(Text, nullable=False)
    county: Mapped[Optional[str]] = mapped_column(Text)
    ttb_approval_date: Mapped[Optional[Date]] = mapped_column(Date)
    total_acres: Mapped[Optional[int]] = mapped_column(Integer)
    planted_acres: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Self-referential hierarchy
    parent: Mapped[Optional["AVA"]] = relationship(
        "AVA", remote_side="AVA.id", back_populates="children"
    )
    children: Mapped[List["AVA"]] = relationship("AVA", back_populates="parent")

    # Relationships
    vineyards: Mapped[List["Vineyard"]] = relationship("Vineyard", back_populates="ava")  # noqa: F821
    wineries: Mapped[List["Winery"]] = relationship("Winery", back_populates="ava")  # noqa: F821
    wines: Mapped[List["Wine"]] = relationship("Wine", back_populates="ava")  # noqa: F821
