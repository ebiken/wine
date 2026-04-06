from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class GrapeVarietyBase(BaseModel):
    key: str
    name: str
    name_synonyms: Optional[str] = None
    color: Optional[str] = None
    origin_region: Optional[str] = None


class GrapeVarietyCreate(GrapeVarietyBase):
    pass


class GrapeVarietyUpdate(BaseModel):
    key: Optional[str] = None
    name: Optional[str] = None
    name_synonyms: Optional[str] = None
    color: Optional[str] = None
    origin_region: Optional[str] = None


class GrapeVarietyRead(GrapeVarietyBase):
    id: int
    model_config = {"from_attributes": True}
