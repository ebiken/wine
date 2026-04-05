from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.grape_variety import GrapeVarietyRead, GrapeVarietyCreate, GrapeVarietyUpdate
import app.crud.grape_variety as crud

router = APIRouter(prefix="/grape-varieties", tags=["Grape Varieties"])


@router.get("/", response_model=List[GrapeVarietyRead])
async def list_grape_varieties(
    color: Optional[str] = Query(None, description="Filter by color: red or white"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_grape_varieties(db, color=color, skip=skip, limit=limit)


@router.get("/{variety_id}", response_model=GrapeVarietyRead)
async def get_grape_variety(variety_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_grape_variety(db, variety_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Grape variety not found")
    return obj


@router.post("/", response_model=GrapeVarietyRead, status_code=201)
async def create_grape_variety(data: GrapeVarietyCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_grape_variety(db, data)


@router.patch("/{variety_id}", response_model=GrapeVarietyRead)
async def update_grape_variety(
    variety_id: int, data: GrapeVarietyUpdate, db: AsyncSession = Depends(get_db)
):
    obj = await crud.update_grape_variety(db, variety_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Grape variety not found")
    return obj


@router.delete("/{variety_id}", status_code=204)
async def delete_grape_variety(variety_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_grape_variety(db, variety_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Grape variety not found")
