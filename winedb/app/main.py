from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.routers import ava, grape_varieties, persons, vineyards, wineries, wines
from app.routers.gui import (
    ava as gui_ava,
    grape_varieties as gui_grape_varieties,
    persons as gui_persons,
    vineyards as gui_vineyards,
    wineries as gui_wineries,
    wines as gui_wines,
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


@app.get("/ui", response_class=HTMLResponse, tags=["UI"])
@app.get("/ui/", response_class=HTMLResponse, tags=["UI"])
async def ui_home(request: Request):
    return templates.TemplateResponse(request, "home.html", {})


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "docs": "/docs", "ui": "/ui/wines"}
