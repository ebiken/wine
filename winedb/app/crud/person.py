from typing import Optional, Sequence
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.person import Person
from app.schemas.person import PersonCreate, PersonUpdate


_PERSON_SORTABLE = {"last_name", "birth_year", "nationality"}


async def get_persons(
    session: AsyncSession,
    search: Optional[str] = None,
    birth_year: Optional[int] = None,
    nationality: Optional[str] = None,
    sort_by: str = "last_name",
    sort_dir: str = "asc",
    skip: int = 0,
    limit: int = 100,
) -> Sequence[Person]:
    q = select(Person)
    if search:
        pattern = f"%{search}%"
        q = q.where(
            or_(
                Person.first_name.ilike(pattern),
                Person.last_name.ilike(pattern),
            )
        )
    if birth_year is not None:
        q = q.where(Person.birth_year == birth_year)
    if nationality:
        q = q.where(Person.nationality.ilike(f"%{nationality}%"))
    col = getattr(Person, sort_by if sort_by in _PERSON_SORTABLE else "last_name")
    order = col.desc() if sort_dir == "desc" else col.asc()
    q = q.offset(skip).limit(limit).order_by(order)
    result = await session.execute(q)
    return result.scalars().all()


async def get_person(session: AsyncSession, person_id: int) -> Optional[Person]:
    result = await session.execute(select(Person).where(Person.id == person_id))
    return result.scalar_one_or_none()


async def create_person(session: AsyncSession, data: PersonCreate) -> Person:
    obj = Person(**data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_person(
    session: AsyncSession, person_id: int, data: PersonUpdate
) -> Optional[Person]:
    obj = await get_person(session, person_id)
    if obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await session.commit()
    await session.refresh(obj)
    return obj


async def delete_person(session: AsyncSession, person_id: int) -> bool:
    obj = await get_person(session, person_id)
    if obj is None:
        return False
    await session.delete(obj)
    await session.commit()
    return True
