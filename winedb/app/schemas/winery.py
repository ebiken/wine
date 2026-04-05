from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel


class WineryStaffRead(BaseModel):
    id: int
    person_id: int
    role: str
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    notes: Optional[str] = None
    model_config = {"from_attributes": True}


class WineryBase(BaseModel):
    name: str
    established_year: Optional[int] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    ava_id: Optional[int] = None
    is_negociant: Optional[bool] = False
    website: Optional[str] = None
    description: Optional[str] = None


class WineryCreate(WineryBase):
    pass


class WineryUpdate(BaseModel):
    name: Optional[str] = None
    established_year: Optional[int] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    ava_id: Optional[int] = None
    is_negociant: Optional[bool] = None
    website: Optional[str] = None
    description: Optional[str] = None


class WineryRead(WineryBase):
    id: int
    model_config = {"from_attributes": True}


class WineryDetail(WineryRead):
    staff: List[WineryStaffRead] = []
    model_config = {"from_attributes": True}
