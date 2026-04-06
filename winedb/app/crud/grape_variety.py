from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grape_variety import GrapeVariety
from app.schemas.grape_variety import GrapeVarietyCreate, GrapeVarietyUpdate


_GV_SORTABLE = {"key", "name", "color", "origin_region"}


async def get_grape_varieties(
    session: AsyncSession,
    color: Optional[str] = None,
    name: Optional[str] = None,
    origin_region: Optional[str] = None,
    sort_by: str = "name",
    sort_dir: str = "asc",
    skip: int = 0,
    limit: int = 100,
) -> Sequence[GrapeVariety]:
    q = select(GrapeVariety)
    if color:
        q = q.where(GrapeVariety.color == color)
    if name:
        q = q.where(GrapeVariety.name.ilike(f"%{name}%"))
    if origin_region:
        q = q.where(GrapeVariety.origin_region.ilike(f"%{origin_region}%"))
    col = getattr(GrapeVariety, sort_by if sort_by in _GV_SORTABLE else "name")
    order = col.desc() if sort_dir == "desc" else col.asc()
    q = q.offset(skip).limit(limit).order_by(order)
    result = await session.execute(q)
    return result.scalars().all()


async def get_grape_variety(
    session: AsyncSession, variety_id: int
) -> Optional[GrapeVariety]:
    result = await session.execute(
        select(GrapeVariety).where(GrapeVariety.id == variety_id)
    )
    return result.scalar_one_or_none()


async def create_grape_variety(
    session: AsyncSession, data: GrapeVarietyCreate
) -> GrapeVariety:
    obj = GrapeVariety(**data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_grape_variety(
    session: AsyncSession, variety_id: int, data: GrapeVarietyUpdate
) -> Optional[GrapeVariety]:
    obj = await get_grape_variety(session, variety_id)
    if obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await session.commit()
    await session.refresh(obj)
    return obj


async def delete_grape_variety(session: AsyncSession, variety_id: int) -> bool:
    obj = await get_grape_variety(session, variety_id)
    if obj is None:
        return False
    await session.delete(obj)
    await session.commit()
    return True
