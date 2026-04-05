from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.vineyard import VineyardRead, VineyardCreate, VineyardUpdate
import app.crud.vineyard as crud

router = APIRouter(prefix="/vineyards", tags=["Vineyards"])


@router.get("/", response_model=List[VineyardRead])
async def list_vineyards(
    ava_id: Optional[int] = Query(None, description="Filter by AVA ID"),
    name: Optional[str] = Query(None, description="Search by vineyard name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_vineyards(db, ava_id=ava_id, name=name, skip=skip, limit=limit)


@router.get("/{vineyard_id}", response_model=VineyardRead)
async def get_vineyard(vineyard_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_vineyard(db, vineyard_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Vineyard not found")
    return obj


@router.post("/", response_model=VineyardRead, status_code=201)
async def create_vineyard(data: VineyardCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_vineyard(db, data)


@router.patch("/{vineyard_id}", response_model=VineyardRead)
async def update_vineyard(
    vineyard_id: int, data: VineyardUpdate, db: AsyncSession = Depends(get_db)
):
    obj = await crud.update_vineyard(db, vineyard_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Vineyard not found")
    return obj


@router.delete("/{vineyard_id}", status_code=204)
async def delete_vineyard(vineyard_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_vineyard(db, vineyard_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vineyard not found")
