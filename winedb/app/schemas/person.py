from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class PersonBase(BaseModel):
    first_name: str
    last_name: str
    birth_year: Optional[int] = None
    nationality: Optional[str] = None
    biography: Optional[str] = None


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_year: Optional[int] = None
    nationality: Optional[str] = None
    biography: Optional[str] = None


class PersonRead(PersonBase):
    id: int
    model_config = {"from_attributes": True}
