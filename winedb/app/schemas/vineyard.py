from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class VineyardBase(BaseModel):
    name: str
    ava_id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation_ft_low: Optional[int] = None
    elevation_ft_high: Optional[int] = None
    total_acres: Optional[int] = None
    soil_type: Optional[str] = None
    established_year: Optional[int] = None
    description: Optional[str] = None


class VineyardCreate(VineyardBase):
    pass


class VineyardUpdate(BaseModel):
    name: Optional[str] = None
    ava_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation_ft_low: Optional[int] = None
    elevation_ft_high: Optional[int] = None
    total_acres: Optional[int] = None
    soil_type: Optional[str] = None
    established_year: Optional[int] = None
    description: Optional[str] = None


class VineyardRead(VineyardBase):
    id: int
    model_config = {"from_attributes": True}
