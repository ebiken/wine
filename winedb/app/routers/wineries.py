from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.winery import WineryRead, WineryDetail, WineryCreate, WineryUpdate
import app.crud.winery as crud

router = APIRouter(prefix="/wineries", tags=["Wineries"])


@router.get("/", response_model=List[WineryRead])
async def list_wineries(
    ava_id: Optional[int] = Query(None, description="Filter by AVA ID"),
    is_negociant: Optional[bool] = Query(None, description="Filter by negociant status"),
    name: Optional[str] = Query(None, description="Search by winery name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_wineries(
        db, ava_id=ava_id, is_negociant=is_negociant, name=name, skip=skip, limit=limit
    )


@router.get("/{winery_id}", response_model=WineryDetail)
async def get_winery(winery_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_winery(db, winery_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Winery not found")
    return obj


@router.post("/", response_model=WineryRead, status_code=201)
async def create_winery(data: WineryCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_winery(db, data)


@router.patch("/{winery_id}", response_model=WineryRead)
async def update_winery(
    winery_id: int, data: WineryUpdate, db: AsyncSession = Depends(get_db)
):
    obj = await crud.update_winery(db, winery_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Winery not found")
    return obj


@router.delete("/{winery_id}", status_code=204)
async def delete_winery(winery_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_winery(db, winery_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Winery not found")
