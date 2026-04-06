"""
Seed data import command.

Usage:
    uv run winedb import data/seed/

Processes YAML files in this order: ava, grape_varieties, persons,
vineyards, vineyard_owner, wineries, winery_staff, wines,
wine_vineyard_sources, wine_grape_variety.

Grape varieties in seed YAML are keyed by stable `key` (see grape_varieties.yaml).
`wines.yaml` primary_variety and `wine_grape_variety.yaml` grape_variety hold those keys.
`vineyards.yaml` grape_variety keys in `grape_varieties` are synced to `vineyard_grape_variety`.
"""

import asyncio
from pathlib import Path
from typing import Any, Optional
from datetime import date

import yaml
import typer
from sqlalchemy import ColumnElement, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import (
    AVA,
    GrapeVariety,
    Person,
    Vineyard,
    Winery,
    Wine,
    WineryStaff,
    WineVineyardSource,
    WineGrapeVariety,
    VineyardOwner,
    VineyardGrapeVariety,
)


def _parse_date(val: Optional[str]) -> Optional[date]:
    if not val:
        return None
    return date.fromisoformat(str(val))


def _nullable_eq_col(col: Any, val: Optional[Any]) -> ColumnElement[bool]:
    """Match a column to a value where YAML/database NULL must align on IS NULL."""
    if val is None:
        return col.is_(None)
    return col == val


async def _resolve_person(session: AsyncSession, prec: dict) -> Optional[Person]:
    result = await session.execute(
        select(Person).where(
            Person.first_name == prec["first_name"],
            Person.last_name == prec["last_name"],
        )
    )
    return result.scalar_one_or_none()


async def _resolve_wine(
    session: AsyncSession, winery_name: str, label_name: str, vintage_year: int
) -> Optional[Wine]:
    winery_result = await session.execute(
        select(Winery).where(Winery.name == winery_name)
    )
    winery = winery_result.scalar_one_or_none()
    if winery is None:
        return None
    result = await session.execute(
        select(Wine).where(
            Wine.winery_id == winery.id,
            Wine.label_name == label_name,
            Wine.vintage_year == vintage_year,
        )
    )
    return result.scalar_one_or_none()


# ---------------------------------------------------------------------------
# Per-entity upsert helpers
# ---------------------------------------------------------------------------

async def _upsert_avas(session: AsyncSession, records: list[dict]) -> None:
    # Two-pass: insert without parent first, then set parent FK
    name_to_id: dict[str, int] = {}

    for rec in records:
        existing = await session.execute(select(AVA).where(AVA.name == rec["name"]))
        obj = existing.scalar_one_or_none()
        if obj is None:
            obj = AVA()
        obj.name = rec["name"]
        obj.short_name = rec.get("short_name")
        obj.state = rec["state"]
        obj.county = rec.get("county")
        obj.ttb_approval_date = _parse_date(rec.get("ttb_approval_date"))
        obj.total_acres = rec.get("total_acres")
        obj.planted_acres = rec.get("planted_acres")
        obj.description = rec.get("description")
        obj.parent_ava_id = None  # resolved in pass 2
        session.add(obj)

    await session.flush()

    # Reload to get IDs
    result = await session.execute(select(AVA))
    for ava in result.scalars().all():
        name_to_id[ava.name] = ava.id

    # Pass 2: set parent FK
    for rec in records:
        parent_name = rec.get("parent_ava")
        if parent_name and parent_name in name_to_id:
            result = await session.execute(select(AVA).where(AVA.name == rec["name"]))
            obj = result.scalar_one()
            obj.parent_ava_id = name_to_id[parent_name]
            session.add(obj)

    await session.flush()


async def _upsert_grape_varieties(session: AsyncSession, records: list[dict]) -> None:
    for rec in records:
        gkey = rec.get("key")
        if not gkey:
            typer.echo(f"  WARNING: Grape variety missing 'key', skipping '{rec.get('name')}'")
            continue
        result = await session.execute(
            select(GrapeVariety).where(GrapeVariety.key == gkey)
        )
        obj = result.scalar_one_or_none()
        if obj is None:
            obj = GrapeVariety()
        obj.key = gkey
        obj.name = rec["name"]
        obj.name_synonyms = rec.get("name_synonyms")
        obj.color = rec.get("color")
        obj.origin_region = rec.get("origin_region")
        session.add(obj)
    await session.flush()


async def _upsert_persons(session: AsyncSession, records: list[dict]) -> None:
    for rec in records:
        result = await session.execute(
            select(Person).where(
                Person.first_name == rec["first_name"],
                Person.last_name == rec["last_name"],
            )
        )
        obj = result.scalar_one_or_none()
        if obj is None:
            obj = Person()
        obj.first_name = rec["first_name"]
        obj.last_name = rec["last_name"]
        obj.birth_year = rec.get("birth_year")
        obj.nationality = rec.get("nationality")
        obj.biography = rec.get("biography")
        session.add(obj)
    await session.flush()


async def _upsert_vineyards(session: AsyncSession, records: list[dict]) -> None:
    for rec in records:
        # Resolve AVA
        ava_result = await session.execute(select(AVA).where(AVA.name == rec["ava"]))
        ava = ava_result.scalar_one_or_none()
        if ava is None:
            typer.echo(f"  WARNING: AVA '{rec['ava']}' not found, skipping vineyard '{rec['name']}'")
            continue

        result = await session.execute(
            select(Vineyard).where(Vineyard.name == rec["name"])
        )
        obj = result.scalar_one_or_none()
        if obj is None:
            obj = Vineyard()
        obj.name = rec["name"]
        obj.ava_id = ava.id
        obj.latitude = rec.get("latitude")
        obj.longitude = rec.get("longitude")
        obj.elevation_ft_low = rec.get("elevation_ft_low")
        obj.elevation_ft_high = rec.get("elevation_ft_high")
        obj.total_acres = rec.get("total_acres")
        obj.soil_type = rec.get("soil_type")
        obj.established_year = rec.get("established_year")
        obj.description = rec.get("description")
        session.add(obj)
        await session.flush()

        await session.execute(
            delete(VineyardGrapeVariety).where(
                VineyardGrapeVariety.vineyard_id == obj.id
            )
        )
        for sort_order, gkey in enumerate(rec.get("grape_varieties") or []):
            gv_result = await session.execute(
                select(GrapeVariety).where(GrapeVariety.key == gkey)
            )
            variety = gv_result.scalar_one_or_none()
            if variety is None:
                typer.echo(
                    f"  WARNING: Grape variety key '{gkey}' not found, "
                    f"skipping for vineyard '{rec['name']}'"
                )
                continue
            session.add(
                VineyardGrapeVariety(
                    vineyard_id=obj.id,
                    grape_variety_id=variety.id,
                    sort_order=sort_order,
                )
            )
    await session.flush()


async def _upsert_wineries(session: AsyncSession, records: list[dict]) -> None:
    for rec in records:
        ava_id = None
        if rec.get("ava"):
            ava_result = await session.execute(
                select(AVA).where(AVA.name == rec["ava"])
            )
            ava = ava_result.scalar_one_or_none()
            if ava:
                ava_id = ava.id
            else:
                typer.echo(f"  WARNING: AVA '{rec['ava']}' not found for winery '{rec['name']}'")

        result = await session.execute(
            select(Winery).where(Winery.name == rec["name"])
        )
        obj = result.scalar_one_or_none()
        if obj is None:
            obj = Winery()
        obj.name = rec["name"]
        obj.established_year = rec.get("established_year")
        obj.location_city = rec.get("location_city")
        obj.location_state = rec.get("location_state")
        obj.ava_id = ava_id
        obj.is_negociant = rec.get("is_negociant", False)
        obj.website = rec.get("website")
        obj.description = rec.get("description")
        session.add(obj)
    await session.flush()


async def _upsert_wines(session: AsyncSession, records: list[dict]) -> None:
    for rec in records:
        # Resolve winery
        winery_result = await session.execute(
            select(Winery).where(Winery.name == rec["winery"])
        )
        winery = winery_result.scalar_one_or_none()
        if winery is None:
            typer.echo(f"  WARNING: Winery '{rec['winery']}' not found, skipping wine '{rec['label_name']}'")
            continue

        # Resolve AVA
        ava_id = None
        if rec.get("ava"):
            ava_result = await session.execute(
                select(AVA).where(AVA.name == rec["ava"])
            )
            ava = ava_result.scalar_one_or_none()
            if ava:
                ava_id = ava.id

        # Resolve primary grape variety
        variety_id = None
        if rec.get("primary_variety"):
            var_result = await session.execute(
                select(GrapeVariety).where(GrapeVariety.key == rec["primary_variety"])
            )
            variety = var_result.scalar_one_or_none()
            if variety:
                variety_id = variety.id
            else:
                typer.echo(
                    f"  WARNING: Grape variety key '{rec['primary_variety']}' not found "
                    f"for wine '{rec['label_name']}'"
                )

        # Upsert wine
        result = await session.execute(
            select(Wine).where(
                Wine.winery_id == winery.id,
                Wine.label_name == rec["label_name"],
                Wine.vintage_year == rec["vintage_year"],
            )
        )
        wine = result.scalar_one_or_none()
        if wine is None:
            wine = Wine()
        wine.winery_id = winery.id
        wine.label_name = rec["label_name"]
        wine.vintage_year = rec["vintage_year"]
        wine.grape_variety_id = variety_id
        wine.ava_id = ava_id
        wine.alcohol_pct = rec.get("alcohol_pct")
        wine.production_cases = rec.get("production_cases")
        wine.release_date = _parse_date(rec.get("release_date"))
        wine.tasting_notes = rec.get("tasting_notes")
        wine.winery_description = rec.get("winery_description")
        wine.description = rec.get("description")
        session.add(wine)

    await session.flush()


async def _upsert_vineyard_owners(session: AsyncSession, records: list[dict]) -> None:
    for rec in records:
        vyd_result = await session.execute(
            select(Vineyard).where(Vineyard.name == rec["vineyard"])
        )
        vyd = vyd_result.scalar_one_or_none()
        if vyd is None:
            typer.echo(f"  WARNING: Vineyard '{rec['vineyard']}' not found, skipping owner row")
            continue

        person = await _resolve_person(session, rec["person"])
        if person is None:
            typer.echo(
                f"  WARNING: Person '{rec['person'].get('first_name')} "
                f"{rec['person'].get('last_name')}' not found, skipping owner row"
            )
            continue

        own_role = rec.get("ownership_role")
        year_start = rec.get("year_start")
        q = select(VineyardOwner).where(
            VineyardOwner.vineyard_id == vyd.id,
            VineyardOwner.person_id == person.id,
            _nullable_eq_col(VineyardOwner.ownership_role, own_role),
            _nullable_eq_col(VineyardOwner.year_start, year_start),
        )
        result = await session.execute(q)
        obj = result.scalar_one_or_none()
        if obj is None:
            obj = VineyardOwner()
        obj.vineyard_id = vyd.id
        obj.person_id = person.id
        obj.ownership_role = own_role
        obj.year_start = year_start
        obj.year_end = rec.get("year_end")
        session.add(obj)
    await session.flush()


async def _upsert_winery_staff(session: AsyncSession, records: list[dict]) -> None:
    for rec in records:
        winery_result = await session.execute(
            select(Winery).where(Winery.name == rec["winery"])
        )
        winery = winery_result.scalar_one_or_none()
        if winery is None:
            typer.echo(f"  WARNING: Winery '{rec['winery']}' not found, skipping staff row")
            continue

        person = await _resolve_person(session, rec["person"])
        if person is None:
            typer.echo(
                f"  WARNING: Person '{rec['person'].get('first_name')} "
                f"{rec['person'].get('last_name')}' not found, skipping staff row"
            )
            continue

        role = rec["role"]
        year_start = rec.get("year_start")
        q = select(WineryStaff).where(
            WineryStaff.winery_id == winery.id,
            WineryStaff.person_id == person.id,
            WineryStaff.role == role,
            _nullable_eq_col(WineryStaff.year_start, year_start),
        )
        result = await session.execute(q)
        obj = result.scalar_one_or_none()
        if obj is None:
            obj = WineryStaff()
        obj.winery_id = winery.id
        obj.person_id = person.id
        obj.role = role
        obj.year_start = year_start
        obj.year_end = rec.get("year_end")
        obj.notes = rec.get("notes")
        session.add(obj)
    await session.flush()


async def _upsert_wine_vineyard_sources(session: AsyncSession, records: list[dict]) -> None:
    for rec in records:
        wine = await _resolve_wine(
            session, rec["winery"], rec["label_name"], rec["vintage_year"]
        )
        if wine is None:
            typer.echo(
                f"  WARNING: Wine '{rec['label_name']}' ({rec['winery']}, "
                f"{rec['vintage_year']}) not found, skipping vineyard source"
            )
            continue

        vyd_result = await session.execute(
            select(Vineyard).where(Vineyard.name == rec["vineyard"])
        )
        vyd = vyd_result.scalar_one_or_none()
        if vyd is None:
            typer.echo(
                f"  WARNING: Vineyard '{rec['vineyard']}' not found for wine "
                f"'{rec['label_name']}'"
            )
            continue

        block_name = rec.get("block_name")
        q = select(WineVineyardSource).where(
            WineVineyardSource.wine_id == wine.id,
            WineVineyardSource.vineyard_id == vyd.id,
            _nullable_eq_col(WineVineyardSource.block_name, block_name),
        )
        result = await session.execute(q)
        src = result.scalar_one_or_none()
        if src is None:
            src = WineVineyardSource()
        src.wine_id = wine.id
        src.vineyard_id = vyd.id
        src.block_name = block_name
        src.pct_blend = rec.get("pct_blend")
        session.add(src)
    await session.flush()


async def _upsert_wine_grape_varieties(session: AsyncSession, records: list[dict]) -> None:
    for rec in records:
        wine = await _resolve_wine(
            session, rec["winery"], rec["label_name"], rec["vintage_year"]
        )
        if wine is None:
            typer.echo(
                f"  WARNING: Wine '{rec['label_name']}' ({rec['winery']}, "
                f"{rec['vintage_year']}) not found, skipping grape variety row"
            )
            continue

        var_result = await session.execute(
            select(GrapeVariety).where(GrapeVariety.key == rec["grape_variety"])
        )
        variety = var_result.scalar_one_or_none()
        if variety is None:
            typer.echo(
                f"  WARNING: Grape variety key '{rec['grape_variety']}' not found for wine "
                f"'{rec['label_name']}'"
            )
            continue

        result = await session.execute(
            select(WineGrapeVariety).where(
                WineGrapeVariety.wine_id == wine.id,
                WineGrapeVariety.grape_variety_id == variety.id,
            )
        )
        obj = result.scalar_one_or_none()
        if obj is None:
            obj = WineGrapeVariety()
        obj.wine_id = wine.id
        obj.grape_variety_id = variety.id
        obj.pct_blend = rec.get("pct_blend")
        session.add(obj)
    await session.flush()


# ---------------------------------------------------------------------------
# Main import orchestration
# ---------------------------------------------------------------------------

IMPORT_ORDER = [
    ("ava.yaml", _upsert_avas),
    ("grape_varieties.yaml", _upsert_grape_varieties),
    ("persons.yaml", _upsert_persons),
    ("vineyards.yaml", _upsert_vineyards),
    ("vineyard_owner.yaml", _upsert_vineyard_owners),
    ("wineries.yaml", _upsert_wineries),
    ("winery_staff.yaml", _upsert_winery_staff),
    ("wines.yaml", _upsert_wines),
    ("wine_vineyard_sources.yaml", _upsert_wine_vineyard_sources),
    ("wine_grape_variety.yaml", _upsert_wine_grape_varieties),
]


async def _run_import(seed_dir: Path) -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for filename, handler in IMPORT_ORDER:
                filepath = seed_dir / filename
                if not filepath.exists():
                    typer.echo(f"  Skipping {filename} (not found)")
                    continue
                records = yaml.safe_load(filepath.read_text()) or []
                if not records:
                    typer.echo(f"  Skipping {filename} (empty)")
                    continue
                typer.echo(f"  Importing {filename} ({len(records)} records)...")
                await handler(session, records)
                typer.echo(f"    Done.")


def import_seed(
    seed_dir: Path = typer.Argument(
        Path("data/seed"),
        help="Directory containing YAML seed files",
    )
) -> None:
    """Import seed data from YAML files into the database."""
    if not seed_dir.is_dir():
        typer.echo(f"Error: '{seed_dir}' is not a directory", err=True)
        raise typer.Exit(1)

    typer.echo(f"Importing seed data from {seed_dir} ...")
    asyncio.run(_run_import(seed_dir))
    typer.echo("Import complete.")
