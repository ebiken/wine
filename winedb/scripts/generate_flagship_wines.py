"""One-off helper: print YAML wine records for seed data. Not imported by the app."""
from __future__ import annotations

import textwrap

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (label_name, primary_variety_key, vintage_year, ava_override or ...) — ava None = use winery ava
# Fourth element: None = use winery.ava; string = override; use "" for explicit null ava
Flagship = tuple[str, str, int, str | None]

FLAGSHIPS: dict[str, Flagship] = {
    # Already covered in wines.yaml; entries unused (see `covered` in main()).
    "Pisoni Estate": ("—", "pinot_noir", 2021, None),
    "Lucia Vineyards": ("—", "pinot_noir", 2021, None),
    "Morgan Winery": ("—", "pinot_noir", 2021, None),
    "ROAR Wines": ("—", "pinot_noir", 2021, None),
    "Talbott Vineyards": ("—", "chardonnay", 2021, None),
    "Kosta Browne": ("—", "pinot_noir", 2023, None),
    "Hahn Family Wines": ("Hahn Santa Lucia Highlands Pinot Noir", "pinot_noir", 2022, None),
    "Siduri Wines": ("Siduri Santa Lucia Highlands Pinot Noir", "pinot_noir", 2022, "Santa Lucia Highlands"),
    "Testarossa Winery": ("Testarossa Santa Lucia Highlands Pinot Noir", "pinot_noir", 2022, "Santa Lucia Highlands"),
    "Stag's Leap Wine Cellars": ("S.L.V. Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Chateau Montelena": ("The Montelena Estate Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Silver Oak Cellars": ("Napa Valley Cabernet Sauvignon", "cabernet_sauvignon", 2019, "Napa Valley"),
    "Robert Mondavi Winery": ("Oakville Estate Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Opus One": ("Opus One", "cabernet_sauvignon", 2021, None),
    "Far Niente": ("Estate Bottled Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Joseph Phelps Vineyards": ("Insignia", "cabernet_sauvignon", 2021, "Napa Valley"),
    "Duckhorn Vineyards": ("Three Palms Vineyard Merlot", "merlot", 2021, "Napa Valley"),
    "Shafer Vineyards": ("Hillside Select", "cabernet_sauvignon", 2020, None),
    "Schramsberg Vineyards": ("Blanc de Blancs", "chardonnay", 2019, None),
    "Spottswoode Estate Vineyard & Winery": ("Estate Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Cakebread Cellars": ("Benchland Select Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Caymus Vineyards": ("Special Selection Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Grgich Hills Estate": ("Estate Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Heitz Cellar": ("Martha's Vineyard Cabernet Sauvignon", "cabernet_sauvignon", 2018, None),
    "Merryvale Vineyards": ("Profile Proprietary Red", "cabernet_sauvignon", 2019, "Napa Valley"),
    "Hall Wines": ("Kathryn Hall Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Clos du Val": ("Hirondelle Vineyard Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Dominus Estate": ("Dominus", "cabernet_sauvignon", 2020, None),
    "Harlan Estate": ("Harlan Estate", "cabernet_sauvignon", 2019, None),
    "Ridge Vineyards": ("Monte Bello", "cabernet_sauvignon", 2020, None),
    "Kistler Vineyards": ("Cuvée Cathleen Chardonnay", "chardonnay", 2022, None),
    "Williams Selyem": ("Ferrington Vineyard Pinot Noir", "pinot_noir", 2022, None),
    "Rochioli Winery": ("Rochioli Estate Pinot Noir", "pinot_noir", 2022, None),
    "Flowers Vineyard & Winery": ("Sea View Ridge Pinot Noir", "pinot_noir", 2022, None),
    "Paul Hobbs Winery": ("Russian River Valley Pinot Noir", "pinot_noir", 2022, None),
    "DuMOL": ("Finn Pinot Noir", "pinot_noir", 2022, None),
    "Bedrock Wine Co.": ("Old Vine Zinfandel", "zinfandel", 2022, "Sonoma Valley"),
    "Scribe Winery": ("Estate Riesling", "riesling", 2023, None),
    "Massican": ("Annia White Wine", "sauvignon_blanc", 2023, "Napa Valley"),
    "Au Bon Climat": ("Isabelle Pinot Noir", "pinot_noir", 2022, None),
    "Sanford Winery": ("Sanford & Benedict Vineyard Pinot Noir", "pinot_noir", 2022, None),
    "Brewer-Clifton": ("3D Pinot Noir", "pinot_noir", 2022, None),
    "Foxen Vineyard & Winery": ("Bien Nacido Vineyard Pinot Noir", "pinot_noir", 2022, "Santa Maria Valley"),
    "Tablas Creek Vineyard": ("Esprit de Tablas", "grenache", 2022, None),
    "Saxum Vineyards": ("James Berry Vineyard G-S-M", "grenache", 2021, None),
    "Justin Vineyards & Winery": ("Isosceles", "cabernet_sauvignon", 2021, None),
    "DAOU Vineyards": ("Soul of a Lion", "cabernet_sauvignon", 2021, None),
    "Alban Vineyards": ("Lorraine Estate Syrah", "syrah", 2021, None),
    "Talley Vineyards": ("Rincon Vineyard Pinot Noir", "pinot_noir", 2022, None),
    "MacRostie Winery": ("Wildcat Mountain Pinot Noir", "pinot_noir", 2022, None),
    "Jordan Vineyard & Winery": ("Alexander Valley Cabernet Sauvignon", "cabernet_sauvignon", 2019, None),
    "Ferrari-Carano Vineyards and Winery": ("Tresor", "cabernet_sauvignon", 2019, None),
    "Rodney Strong Vineyards": ("Alexander Valley Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Dry Creek Vineyard": ("Heritage Zinfandel", "zinfandel", 2022, None),
    "Turley Wine Cellars": ("Hayne Vineyard Zinfandel", "zinfandel", 2021, "Napa Valley"),
    "Darioush Winery": ("Signature Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Beringer Vineyards": ("Private Reserve Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Charles Krug Winery": ("Family Reserve Generations", "cabernet_sauvignon", 2020, None),
    "Inglenook": ("Rubicon", "cabernet_sauvignon", 2019, None),
    "Trefethen Family Vineyards": ("Estate Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Domaine Carneros": ("Le Rêve Blanc de Blancs", "chardonnay", 2018, None),
    "St. Supéry Estate Vineyards & Winery": ("Dollarhide Estate Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Frank Family Vineyards": ("Rutherford Reserve Cabernet Sauvignon", "cabernet_sauvignon", 2021, None),
    "Peay Vineyards": ("Scallop Shelf Pinot Noir", "pinot_noir", 2022, None),
    "Domaine Drouhin Oregon": ("Laurene Pinot Noir", "pinot_noir", 2022, None),
    "Domaine Serene": ("Evenstad Reserve Pinot Noir", "pinot_noir", 2021, None),
    "Argyle Winery": ("Extended Tirage Brut", "pinot_noir", 2015, "Willamette Valley"),
    "Archery Summit": ("Arcus Pinot Noir", "pinot_noir", 2021, None),
    "Evening Land Vineyards": ("Seven Springs Vineyard Pinot Noir", "pinot_noir", 2021, None),
    "Cristom Vineyards": ("Marjorie Vineyard Pinot Noir", "pinot_noir", 2022, None),
    "Ken Wright Cellars": ("Canary Hill Vineyard Pinot Noir", "pinot_noir", 2022, None),
    "Bergström Wines": ("Silice Pinot Noir", "pinot_noir", 2021, None),
    "Beaux Frères": ("Beaux Frères Vineyard Pinot Noir", "pinot_noir", 2022, None),
    "Ponzi Vineyards": ("Laurelwood Pinot Noir", "pinot_noir", 2022, None),
    "Adelsheim Vineyard": ("Caitlin's Reserve Pinot Noir", "pinot_noir", 2021, None),
    "The Eyrie Vineyards": ("Original Vines Pinot Noir", "pinot_noir", 2018, None),
    "Sokol Blosser Winery": ("Big Tree Block Pinot Noir", "pinot_noir", 2022, None),
    "St. Innocent Winery": ("Shea Vineyard Pinot Noir", "pinot_noir", 2022, None),
    "Patricia Green Cellars": ("Balcombe Vineyard Pinot Noir", "pinot_noir", 2022, None),
    "ROCO Winery": ("RMS Brut", "chardonnay", 2018, "Willamette Valley"),
    "Lingua Franca": ("Estate Pinot Noir", "pinot_noir", 2021, None),
    "Nicolas-Jay": ("Own Rooted Pinot Noir", "pinot_noir", 2021, None),
    "Soter Vineyards": ("Mineral Springs Ranch Pinot Noir", "pinot_noir", 2022, None),
    "Bethel Heights Vineyard": ("Casteel Pinot Noir", "pinot_noir", 2021, None),
    "A to Z Wineworks": ("The Essence of Oregon Pinot Noir", "pinot_noir", 2022, "Willamette Valley"),
    "Willamette Valley Vineyards": ("Whole Cluster Pinot Noir", "pinot_noir", 2022, None),
    "Brooks Wine": ("Janus Pinot Noir", "pinot_noir", 2021, None),
    "Gran Moraine": ("Brut Rosé", "pinot_noir", 2019, None),
    "Walter Scott Wines": ("La Combe Verte Pinot Noir", "pinot_noir", 2022, None),
    "White Rose Estate": ("White Rose Pinot Noir", "pinot_noir", 2021, None),
    "Antica Terra": ("Estate Pinot Noir", "pinot_noir", 2021, None),
    "Brick House Vineyards": ("Gamay Noir", "gamay", 2022, None),
    "Colene Clemens Vineyards": ("Adriane Vineyard Pinot Noir", "pinot_noir", 2022, None),
    "Résonance": ("Résonance Vineyard Pinot Noir", "pinot_noir", 2021, None),
    "Sequitur": ("Estate Pinot Noir", "pinot_noir", 2021, None),
    "Brittan Vineyards": ("Gestalt Block Pinot Noir", "pinot_noir", 2022, None),
    "The Four Graces": ("Dundee Hills Pinot Noir", "pinot_noir", 2022, None),
    "Lemelson Vineyards": ("Thea's Selection Pinot Noir", "pinot_noir", 2022, None),
    "Trisaetum Winery": ("Estate Riesling", "riesling", 2023, None),
    "Ovum Wines": ("Big Salt", "riesling", 2023, "Willamette Valley"),
}

# Second labels / extra majors for wineries that already had seed wines
EXTRAS: list[tuple[str, Flagship]] = [
    ("Pisoni Estate", ("Pisoni Estate Chardonnay", "chardonnay", 2022, None)),
    ("Lucia Vineyards", ("Lucia Syrah Soberanes Vineyard", "syrah", 2021, "Santa Lucia Highlands")),
    ("Morgan Winery", ("Morgan Twelve Clones Syrah", "syrah", 2021, "Santa Lucia Highlands")),
    ("ROAR Wines", ("ROAR Syrah Rosella's Vineyard", "syrah", 2021, "Santa Lucia Highlands")),
    ("Talbott Vineyards", ("Talbott Sleepy Hollow Vineyard Pinot Noir", "pinot_noir", 2021, None)),
    ("Kosta Browne", ("Kosta Browne Russian River Valley Pinot Noir", "pinot_noir", 2023, "Russian River Valley")),
]


def _yaml_double_quoted(s: str) -> str:
    return yaml.dump(s, default_style='"', width=999).strip()


def wine_yaml_block(
    winery_name: str,
    label_name: str,
    primary_variety: str,
    vintage_year: int,
    ava: str | None,
    winery_description: str,
) -> str:
    ava_line = "null" if ava is None else _yaml_double_quoted(ava)
    desc = textwrap.dedent(winery_description).strip()
    wrapped = textwrap.wrap(desc, width=74) or [""]
    folded_yaml = "\n".join(f"    {ln}" for ln in wrapped)
    return f"""- label_name: {_yaml_double_quoted(label_name)}
  winery: {_yaml_double_quoted(winery_name)}
  vintage_year: {vintage_year}
  primary_variety: {primary_variety}
  ava: {ava_line}
  alcohol_pct: null
  production_cases: null
  release_date: null
  tasting_notes: null
  winery_description: >
{folded_yaml}
  description: null

"""


def main() -> None:
    wineries = yaml.safe_load((ROOT / "data/seed/wineries.yaml").read_text())
    by_name = {w["name"]: w for w in wineries}
    existing = yaml.safe_load((ROOT / "data/seed/wines.yaml").read_text())
    covered = {r["winery"] for r in existing}

    chunks: list[str] = []
    for w in wineries:
        name = w["name"]
        if name not in FLAGSHIPS:
            raise SystemExit(f"Missing FLAGSHIPS entry for: {name!r}")
        label, variety, vintage, ava_ov = FLAGSHIPS[name]
        if ava_ov is None:
            ava = w.get("ava")
        elif ava_ov == "":
            ava = None
        else:
            ava = ava_ov
        raw = (w.get("description") or "").replace("\n", " ").strip()
        if len(raw) > 450:
            raw = raw[:450].rsplit(" ", 1)[0] + "..."
        desc = f"Flagship {variety} program from {name}. {raw}".strip()
        if name not in covered:
            chunks.append(wine_yaml_block(name, label, variety, vintage, ava, desc))

    for winery_name, (label, variety, vintage, ava_ov) in EXTRAS:
        w = by_name[winery_name]
        if ava_ov is None:
            ava = w.get("ava")
        elif ava_ov == "":
            ava = None
        else:
            ava = ava_ov
        raw = (w.get("description") or "").replace("\n", " ").strip()
        if len(raw) > 450:
            raw = raw[:450].rsplit(" ", 1)[0] + "..."
        desc = f"Notable {variety} bottling from {winery_name}. {raw}".strip()
        chunks.append(wine_yaml_block(winery_name, label, variety, vintage, ava, desc))

    print(
        "# Major wines — flagship and notable bottlings (curated). "
        "Add fruit sourcing rows in wine_vineyard_sources.yaml when needed."
    )
    print("".join(chunks).rstrip() + "\n")


if __name__ == "__main__":
    main()
