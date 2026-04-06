from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.associations import WineGrapeVariety
from app.models.grape_variety import GrapeVariety
from app.models.wine import Wine
from app.models.winery import Winery

_SORTABLE = {
    "winery_name": Winery.name,
    "label_name": Wine.label_name,
    "vintage_year": Wine.vintage_year,
    "grape_name": GrapeVariety.name,
    "pct_blend": WineGrapeVariety.pct_blend,
}


async def get_wine_grape_varieties(
    session: AsyncSession,
    label_search: Optional[str] = None,
    winery_search: Optional[str] = None,
    grape_search: Optional[str] = None,
    sort_by: str = "winery_name",
    sort_dir: str = "asc",
    skip: int = 0,
    limit: int = 500,
) -> Sequence[WineGrapeVariety]:
    q = (
        select(WineGrapeVariety)
        .join(WineGrapeVariety.wine)
        .join(Wine.winery)
        .join(WineGrapeVariety.grape_variety)
        .options(
            contains_eager(WineGrapeVariety.wine).contains_eager(Wine.winery),
            contains_eager(WineGrapeVariety.grape_variety),
        )
    )
    if label_search:
        q = q.where(Wine.label_name.ilike(f"%{label_search}%"))
    if winery_search:
        q = q.where(Winery.name.ilike(f"%{winery_search}%"))
    if grape_search:
        q = q.where(GrapeVariety.name.ilike(f"%{grape_search}%"))

    col = _SORTABLE.get(sort_by, Winery.name)
    order = col.desc() if sort_dir == "desc" else col.asc()
    q = (
        q.order_by(order, Wine.label_name, Wine.vintage_year, GrapeVariety.name)
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(q)
    return result.scalars().unique().all()
