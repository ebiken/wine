from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.ava import AVARead, AVADetail, AVACreate, AVAUpdate
import app.crud.ava as crud

router = APIRouter(prefix="/ava", tags=["AVA"])


@router.get("/", response_model=List[AVARead])
async def list_avas(
    state: Optional[str] = Query(None, description="Filter by state code, e.g. CA"),
    parent_ava_id: Optional[int] = Query(None, description="Filter by parent AVA ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_avas(db, state=state, parent_ava_id=parent_ava_id, skip=skip, limit=limit)


@router.get("/{ava_id}", response_model=AVADetail)
async def get_ava(ava_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_ava(db, ava_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="AVA not found")
    return obj


@router.post("/", response_model=AVARead, status_code=201)
async def create_ava(data: AVACreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_ava(db, data)


@router.patch("/{ava_id}", response_model=AVARead)
async def update_ava(ava_id: int, data: AVAUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud.update_ava(db, ava_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="AVA not found")
    return obj


@router.delete("/{ava_id}", status_code=204)
async def delete_ava(ava_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_ava(db, ava_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="AVA not found")
