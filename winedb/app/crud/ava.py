from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ava import AVA
from app.schemas.ava import AVACreate, AVAUpdate


_AVA_SORTABLE = {"name", "state", "total_acres"}


async def get_avas(
    session: AsyncSession,
    state: Optional[str] = None,
    parent_ava_id: Optional[int] = None,
    name: Optional[str] = None,
    county: Optional[str] = None,
    sort_by: str = "name",
    sort_dir: str = "asc",
    skip: int = 0,
    limit: int = 100,
) -> Sequence[AVA]:
    q = select(AVA)
    if state:
        q = q.where(AVA.state == state)
    if parent_ava_id is not None:
        q = q.where(AVA.parent_ava_id == parent_ava_id)
    if name:
        q = q.where(AVA.name.ilike(f"%{name}%"))
    if county:
        q = q.where(AVA.county.ilike(f"%{county}%"))
    col = getattr(AVA, sort_by if sort_by in _AVA_SORTABLE else "name")
    order = col.desc() if sort_dir == "desc" else col.asc()
    q = q.offset(skip).limit(limit).order_by(order)
    result = await session.execute(q)
    return result.scalars().all()


async def get_ava(session: AsyncSession, ava_id: int) -> Optional[AVA]:
    result = await session.execute(
        select(AVA).where(AVA.id == ava_id).options(selectinload(AVA.children))
    )
    return result.scalar_one_or_none()


async def create_ava(session: AsyncSession, data: AVACreate) -> AVA:
    obj = AVA(**data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_ava(
    session: AsyncSession, ava_id: int, data: AVAUpdate
) -> Optional[AVA]:
    obj = await get_ava(session, ava_id)
    if obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await session.commit()
    await session.refresh(obj)
    return obj


async def delete_ava(session: AsyncSession, ava_id: int) -> bool:
    obj = await get_ava(session, ava_id)
    if obj is None:
        return False
    await session.delete(obj)
    await session.commit()
    return True
