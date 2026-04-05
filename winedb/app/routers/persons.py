from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.person import PersonRead, PersonCreate, PersonUpdate
import app.crud.person as crud

router = APIRouter(prefix="/persons", tags=["Persons"])


@router.get("/", response_model=List[PersonRead])
async def list_persons(
    search: Optional[str] = Query(None, description="Search by first or last name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_persons(db, search=search, skip=skip, limit=limit)


@router.get("/{person_id}", response_model=PersonRead)
async def get_person(person_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_person(db, person_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return obj


@router.post("/", response_model=PersonRead, status_code=201)
async def create_person(data: PersonCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_person(db, data)


@router.patch("/{person_id}", response_model=PersonRead)
async def update_person(
    person_id: int, data: PersonUpdate, db: AsyncSession = Depends(get_db)
):
    obj = await crud.update_person(db, person_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return obj


@router.delete("/{person_id}", status_code=204)
async def delete_person(person_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_person(db, person_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Person not found")
