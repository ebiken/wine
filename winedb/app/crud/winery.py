from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.winery import Winery
from app.models.associations import WineryStaff
from app.schemas.winery import WineryCreate, WineryUpdate


_WINERY_SORTABLE = {"name", "established_year"}


async def get_wineries(
    session: AsyncSession,
    ava_id: Optional[int] = None,
    is_negociant: Optional[bool] = None,
    name: Optional[str] = None,
    location: Optional[str] = None,
    established_year: Optional[int] = None,
    sort_by: str = "name",
    sort_dir: str = "asc",
    skip: int = 0,
    limit: int = 100,
) -> Sequence[Winery]:
    q = select(Winery)
    if ava_id is not None:
        q = q.where(Winery.ava_id == ava_id)
    if is_negociant is not None:
        q = q.where(Winery.is_negociant == is_negociant)
    if name:
        q = q.where(Winery.name.ilike(f"%{name}%"))
    if location:
        q = q.where(
            Winery.location_city.ilike(f"%{location}%") |
            Winery.location_state.ilike(f"%{location}%")
        )
    if established_year is not None:
        q = q.where(Winery.established_year == established_year)
    col = getattr(Winery, sort_by if sort_by in _WINERY_SORTABLE else "name")
    order = col.desc() if sort_dir == "desc" else col.asc()
    q = q.offset(skip).limit(limit).order_by(order)
    result = await session.execute(q)
    return result.scalars().all()


async def get_winery(session: AsyncSession, winery_id: int) -> Optional[Winery]:
    result = await session.execute(
        select(Winery)
        .where(Winery.id == winery_id)
        .options(selectinload(Winery.staff))
    )
    return result.scalar_one_or_none()


async def create_winery(session: AsyncSession, data: WineryCreate) -> Winery:
    obj = Winery(**data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_winery(
    session: AsyncSession, winery_id: int, data: WineryUpdate
) -> Optional[Winery]:
    obj = await get_winery(session, winery_id)
    if obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await session.commit()
    await session.refresh(obj)
    return obj


async def delete_winery(session: AsyncSession, winery_id: int) -> bool:
    obj = await get_winery(session, winery_id)
    if obj is None:
        return False
    await session.delete(obj)
    await session.commit()
    return True
