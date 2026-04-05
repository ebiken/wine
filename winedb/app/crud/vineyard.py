from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vineyard import Vineyard
from app.schemas.vineyard import VineyardCreate, VineyardUpdate


async def get_vineyards(
    session: AsyncSession,
    ava_id: Optional[int] = None,
    name: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[Vineyard]:
    q = select(Vineyard)
    if ava_id is not None:
        q = q.where(Vineyard.ava_id == ava_id)
    if name:
        q = q.where(Vineyard.name.ilike(f"%{name}%"))
    q = q.offset(skip).limit(limit).order_by(Vineyard.name)
    result = await session.execute(q)
    return result.scalars().all()


async def get_vineyard(session: AsyncSession, vineyard_id: int) -> Optional[Vineyard]:
    result = await session.execute(
        select(Vineyard).where(Vineyard.id == vineyard_id)
    )
    return result.scalar_one_or_none()


async def create_vineyard(session: AsyncSession, data: VineyardCreate) -> Vineyard:
    obj = Vineyard(**data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_vineyard(
    session: AsyncSession, vineyard_id: int, data: VineyardUpdate
) -> Optional[Vineyard]:
    obj = await get_vineyard(session, vineyard_id)
    if obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await session.commit()
    await session.refresh(obj)
    return obj


async def delete_vineyard(session: AsyncSession, vineyard_id: int) -> bool:
    obj = await get_vineyard(session, vineyard_id)
    if obj is None:
        return False
    await session.delete(obj)
    await session.commit()
    return True
