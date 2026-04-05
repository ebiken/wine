from __future__ import annotations
from datetime import date
from typing import Optional, List
from pydantic import BaseModel


class VineyardSourceRead(BaseModel):
    vineyard_id: int
    vineyard_name: Optional[str] = None
    block_name: Optional[str] = None
    pct_blend: Optional[float] = None
    model_config = {"from_attributes": True}


class WineBase(BaseModel):
    winery_id: int
    label_name: str
    vintage_year: int
    grape_variety_id: Optional[int] = None
    ava_id: Optional[int] = None
    alcohol_pct: Optional[float] = None
    production_cases: Optional[int] = None
    release_date: Optional[date] = None
    tasting_notes: Optional[str] = None
    winery_description: Optional[str] = None
    description: Optional[str] = None


class WineCreate(WineBase):
    pass


class WineUpdate(BaseModel):
    label_name: Optional[str] = None
    vintage_year: Optional[int] = None
    grape_variety_id: Optional[int] = None
    ava_id: Optional[int] = None
    alcohol_pct: Optional[float] = None
    production_cases: Optional[int] = None
    release_date: Optional[date] = None
    tasting_notes: Optional[str] = None
    winery_description: Optional[str] = None
    description: Optional[str] = None


class WineRead(WineBase):
    id: int
    model_config = {"from_attributes": True}


class WineDetail(WineRead):
    vineyard_sources: List[VineyardSourceRead] = []
    model_config = {"from_attributes": True}
