from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.associations import WineVineyardSource
from app.models.vineyard import Vineyard
from app.models.wine import Wine
from app.models.winery import Winery

_SORTABLE = {
    "winery_name": Winery.name,
    "label_name": Wine.label_name,
    "vintage_year": Wine.vintage_year,
    "vineyard_name": Vineyard.name,
    "pct_blend": WineVineyardSource.pct_blend,
}


async def get_wine_vineyard_sources(
    session: AsyncSession,
    label_search: Optional[str] = None,
    winery_search: Optional[str] = None,
    vineyard_search: Optional[str] = None,
    sort_by: str = "winery_name",
    sort_dir: str = "asc",
    skip: int = 0,
    limit: int = 500,
) -> Sequence[WineVineyardSource]:
    q = (
        select(WineVineyardSource)
        .join(WineVineyardSource.wine)
        .join(Wine.winery)
        .join(WineVineyardSource.vineyard)
        .options(
            contains_eager(WineVineyardSource.wine).contains_eager(Wine.winery),
            contains_eager(WineVineyardSource.vineyard),
        )
    )
    if label_search:
        q = q.where(Wine.label_name.ilike(f"%{label_search}%"))
    if winery_search:
        q = q.where(Winery.name.ilike(f"%{winery_search}%"))
    if vineyard_search:
        q = q.where(Vineyard.name.ilike(f"%{vineyard_search}%"))

    col = _SORTABLE.get(sort_by, Winery.name)
    order = col.desc() if sort_dir == "desc" else col.asc()
    q = (
        q.order_by(order, Wine.label_name, Wine.vintage_year, Vineyard.name)
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(q)
    return result.scalars().unique().all()
