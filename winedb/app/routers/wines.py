from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.associations import WineVineyardSource
from app.models.vineyard import Vineyard
from app.schemas.wine import WineRead, WineDetail, WineCreate, WineUpdate, VineyardSourceRead
import app.crud.wine as crud

router = APIRouter(prefix="/wines", tags=["Wines"])


@router.get("/", response_model=List[WineRead])
async def list_wines(
    winery_id: Optional[int] = Query(None),
    ava_id: Optional[int] = Query(None),
    vintage_year: Optional[int] = Query(None),
    grape_variety_id: Optional[int] = Query(None),
    label_name: Optional[str] = Query(None, description="Search by label name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_wines(
        db,
        winery_id=winery_id,
        ava_id=ava_id,
        vintage_year=vintage_year,
        grape_variety_id=grape_variety_id,
        label_name=label_name,
        skip=skip,
        limit=limit,
    )


@router.get("/{wine_id}", response_model=WineDetail)
async def get_wine(wine_id: int, db: AsyncSession = Depends(get_db)):
    wine = await crud.get_wine(db, wine_id)
    if wine is None:
        raise HTTPException(status_code=404, detail="Wine not found")

    # Enrich vineyard sources with vineyard names
    sources = []
    for src in wine.vineyard_sources:
        vyd_result = await db.execute(
            select(Vineyard).where(Vineyard.id == src.vineyard_id)
        )
        vyd = vyd_result.scalar_one_or_none()
        sources.append(
            VineyardSourceRead(
                vineyard_id=src.vineyard_id,
                vineyard_name=vyd.name if vyd else None,
                block_name=src.block_name,
                pct_blend=src.pct_blend,
            )
        )

    detail = WineDetail.model_validate(wine)
    detail.vineyard_sources = sources
    return detail


@router.post("/", response_model=WineRead, status_code=201)
async def create_wine(data: WineCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_wine(db, data)


@router.patch("/{wine_id}", response_model=WineRead)
async def update_wine(
    wine_id: int, data: WineUpdate, db: AsyncSession = Depends(get_db)
):
    obj = await crud.update_wine(db, wine_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Wine not found")
    return obj


@router.delete("/{wine_id}", status_code=204)
async def delete_wine(wine_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_wine(db, wine_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Wine not found")
