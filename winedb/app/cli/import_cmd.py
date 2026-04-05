"""
Seed data import command.

Usage:
    uv run winedb import data/seed/

Processes YAML files in this order: ava, grape_varieties, persons,
vineyards, wineries, wines.
"""

import asyncio
from pathlib import Path
from typing import Optional
from datetime import date

import yaml
import typer
from sqlalchemy import select
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
    VineyardOwner,
)


def _parse_date(val: Optional[str]) -> Optional[date]:
    if not val:
        return None
    return date.fromisoformat(str(val))


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
        result = await session.execute(
            select(GrapeVariety).where(GrapeVariety.name == rec["name"])
        )
        obj = result.scalar_one_or_none()
        if obj is None:
            obj = GrapeVariety()
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
                select(GrapeVariety).where(GrapeVariety.name == rec["primary_variety"])
            )
            variety = var_result.scalar_one_or_none()
            if variety:
                variety_id = variety.id
            else:
                typer.echo(f"  WARNING: Variety '{rec['primary_variety']}' not found for wine '{rec['label_name']}'")

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

        # Vineyard sources
        for vsrc in rec.get("vineyard_sources", []):
            vyd_result = await session.execute(
                select(Vineyard).where(Vineyard.name == vsrc["vineyard"])
            )
            vyd = vyd_result.scalar_one_or_none()
            if vyd is None:
                typer.echo(f"  WARNING: Vineyard '{vsrc['vineyard']}' not found for wine '{rec['label_name']}'")
                continue

            src_result = await session.execute(
                select(WineVineyardSource).where(
                    WineVineyardSource.wine_id == wine.id,
                    WineVineyardSource.vineyard_id == vyd.id,
                )
            )
            src = src_result.scalar_one_or_none()
            if src is None:
                src = WineVineyardSource()
            src.wine_id = wine.id
            src.vineyard_id = vyd.id
            src.block_name = vsrc.get("block_name")
            src.pct_blend = vsrc.get("pct_blend")
            session.add(src)

    await session.flush()


# ---------------------------------------------------------------------------
# Main import orchestration
# ---------------------------------------------------------------------------

IMPORT_ORDER = [
    ("ava.yaml", _upsert_avas),
    ("grape_varieties.yaml", _upsert_grape_varieties),
    ("persons.yaml", _upsert_persons),
    ("vineyards.yaml", _upsert_vineyards),
    ("wineries.yaml", _upsert_wineries),
    ("wines.yaml", _upsert_wines),
]


async def _run_import(seed_dir: Path) -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for filename, handler in IMPORT_ORDER:
                filepath = seed_dir / filename
                if not filepath.exists():
                    typer.echo(f"  Skipping {filename} (not found)")
                    continue
                records = yaml.safe_load(filepath.read_text())
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
