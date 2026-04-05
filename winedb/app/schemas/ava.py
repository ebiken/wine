from __future__ import annotations
from datetime import date
from typing import Optional, List
from pydantic import BaseModel


class AVABase(BaseModel):
    name: str
    short_name: Optional[str] = None
    parent_ava_id: Optional[int] = None
    state: str
    county: Optional[str] = None
    ttb_approval_date: Optional[date] = None
    total_acres: Optional[int] = None
    planted_acres: Optional[int] = None
    description: Optional[str] = None


class AVACreate(AVABase):
    pass


class AVAUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    parent_ava_id: Optional[int] = None
    state: Optional[str] = None
    county: Optional[str] = None
    ttb_approval_date: Optional[date] = None
    total_acres: Optional[int] = None
    planted_acres: Optional[int] = None
    description: Optional[str] = None


class AVARead(AVABase):
    id: int
    model_config = {"from_attributes": True}


class AVADetail(AVARead):
    children: List[AVARead] = []
    model_config = {"from_attributes": True}
