from typing import Optional, Sequence

from sqlalchemy import or_, select
from sqlalchemy.orm import contains_eager
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.associations import WineryStaff
from app.models.person import Person
from app.models.winery import Winery

_SORTABLE = {
    "winery_name": Winery.name,
    "person_last": Person.last_name,
    "role": WineryStaff.role,
    "year_start": WineryStaff.year_start,
}


async def get_winery_staff(
    session: AsyncSession,
    winery_search: Optional[str] = None,
    person_search: Optional[str] = None,
    role_search: Optional[str] = None,
    sort_by: str = "winery_name",
    sort_dir: str = "asc",
    skip: int = 0,
    limit: int = 500,
) -> Sequence[WineryStaff]:
    q = (
        select(WineryStaff)
        .join(WineryStaff.winery)
        .join(WineryStaff.person)
        .options(
            contains_eager(WineryStaff.winery),
            contains_eager(WineryStaff.person),
        )
    )
    if winery_search:
        q = q.where(Winery.name.ilike(f"%{winery_search}%"))
    if person_search:
        pat = f"%{person_search}%"
        q = q.where(
            or_(
                Person.first_name.ilike(pat),
                Person.last_name.ilike(pat),
            )
        )
    if role_search:
        q = q.where(WineryStaff.role.ilike(f"%{role_search}%"))

    col = _SORTABLE.get(sort_by, Winery.name)
    order = col.desc() if sort_dir == "desc" else col.asc()
    q = q.order_by(order, Person.last_name, Person.first_name).offset(skip).limit(limit)
    result = await session.execute(q)
    return result.scalars().unique().all()
