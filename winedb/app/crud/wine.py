from typing import Optional, Sequence
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.wine import Wine
from app.models.associations import WineVineyardSource
from app.schemas.wine import WineCreate, WineUpdate


async def get_wines(
    session: AsyncSession,
    winery_id: Optional[int] = None,
    ava_id: Optional[int] = None,
    vintage_year: Optional[int] = None,
    grape_variety_id: Optional[int] = None,
    label_name: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[Wine]:
    q = select(Wine).options(selectinload(Wine.vineyard_sources))
    if winery_id is not None:
        q = q.where(Wine.winery_id == winery_id)
    if ava_id is not None:
        q = q.where(Wine.ava_id == ava_id)
    if vintage_year is not None:
        q = q.where(Wine.vintage_year == vintage_year)
    if grape_variety_id is not None:
        q = q.where(Wine.grape_variety_id == grape_variety_id)
    if label_name:
        q = q.where(Wine.label_name.ilike(f"%{label_name}%"))
    q = q.offset(skip).limit(limit).order_by(Wine.vintage_year.desc(), Wine.label_name)
    result = await session.execute(q)
    return result.scalars().all()


async def get_wine(session: AsyncSession, wine_id: int) -> Optional[Wine]:
    result = await session.execute(
        select(Wine)
        .where(Wine.id == wine_id)
        .options(selectinload(Wine.vineyard_sources))
    )
    return result.scalar_one_or_none()


async def create_wine(session: AsyncSession, data: WineCreate) -> Wine:
    obj = Wine(**data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_wine(
    session: AsyncSession, wine_id: int, data: WineUpdate
) -> Optional[Wine]:
    obj = await get_wine(session, wine_id)
    if obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await session.commit()
    await session.refresh(obj)
    return obj


async def delete_wine(session: AsyncSession, wine_id: int) -> bool:
    obj = await get_wine(session, wine_id)
    if obj is None:
        return False
    await session.delete(obj)
    await session.commit()
    return True


async def replace_vineyard_sources(
    session: AsyncSession,
    wine_id: int,
    sources: list[dict],
) -> None:
    """Delete all existing WineVineyardSource rows for wine_id and insert new ones."""
    await session.execute(
        delete(WineVineyardSource).where(WineVineyardSource.wine_id == wine_id)
    )
    for src in sources:
        session.add(WineVineyardSource(
            wine_id=wine_id,
            vineyard_id=src["vineyard_id"],
            block_name=src.get("block_name") or None,
            pct_blend=src.get("pct_blend"),
        ))
    await session.commit()
