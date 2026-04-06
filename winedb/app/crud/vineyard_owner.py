from typing import Optional, Sequence

from sqlalchemy import or_, select
from sqlalchemy.orm import contains_eager
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.associations import VineyardOwner
from app.models.person import Person
from app.models.vineyard import Vineyard

_SORTABLE = {
    "vineyard_name": Vineyard.name,
    "person_last": Person.last_name,
    "ownership_role": VineyardOwner.ownership_role,
    "year_start": VineyardOwner.year_start,
}


async def get_vineyard_owners(
    session: AsyncSession,
    vineyard_search: Optional[str] = None,
    person_search: Optional[str] = None,
    role_search: Optional[str] = None,
    sort_by: str = "vineyard_name",
    sort_dir: str = "asc",
    skip: int = 0,
    limit: int = 500,
) -> Sequence[VineyardOwner]:
    q = (
        select(VineyardOwner)
        .join(VineyardOwner.vineyard)
        .join(VineyardOwner.person)
        .options(
            contains_eager(VineyardOwner.vineyard),
            contains_eager(VineyardOwner.person),
        )
    )
    if vineyard_search:
        q = q.where(Vineyard.name.ilike(f"%{vineyard_search}%"))
    if person_search:
        pat = f"%{person_search}%"
        q = q.where(
            or_(
                Person.first_name.ilike(pat),
                Person.last_name.ilike(pat),
            )
        )
    if role_search:
        q = q.where(VineyardOwner.ownership_role.ilike(f"%{role_search}%"))

    col = _SORTABLE.get(sort_by, Vineyard.name)
    order = col.desc() if sort_dir == "desc" else col.asc()
    q = q.order_by(order, Person.last_name, Person.first_name).offset(skip).limit(limit)
    result = await session.execute(q)
    return result.scalars().unique().all()
