from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.routers import ava, grape_varieties, persons, vineyards, wineries, wines
from app.routers.gui import (
    ava as gui_ava,
    grape_varieties as gui_grape_varieties,
    persons as gui_persons,
    vineyard_owners as gui_vineyard_owners,
    vineyards as gui_vineyards,
    wineries as gui_wineries,
    wine_grape_varieties as gui_wine_grape_varieties,
    wine_vineyard_sources as gui_wine_vineyard_sources,
    wines as gui_wines,
    winery_staff as gui_winery_staff,
)
from app.templates import templates

app = FastAPI(
    title="WineDB",
    description="Wine database API — AVAs, vineyards, wineries, people, and wines in the United States.",
    version="0.1.0",
)

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)

# JSON API routers
app.include_router(ava.router)
app.include_router(grape_varieties.router)
app.include_router(persons.router)
app.include_router(vineyards.router)
app.include_router(wineries.router)
app.include_router(wines.router)

# GUI routers
app.include_router(gui_grape_varieties.router)
app.include_router(gui_ava.router)
app.include_router(gui_persons.router)
app.include_router(gui_vineyards.router)
app.include_router(gui_wineries.router)
app.include_router(gui_wines.router)
app.include_router(gui_winery_staff.router)
app.include_router(gui_vineyard_owners.router)
app.include_router(gui_wine_vineyard_sources.router)
app.include_router(gui_wine_grape_varieties.router)


@app.get("/ui", response_class=HTMLResponse, tags=["UI"])
@app.get("/ui/", response_class=HTMLResponse, tags=["UI"])
async def ui_home(request: Request):
    return templates.TemplateResponse(request, "home.html", {})


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "docs": "/docs", "ui": "/ui/wines"}
