from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/classification-schemes", tags=["Classification Schemes"])


@router.get("", response_model=schemas.Page[schemas.ClassificationSchemeRead], summary="List classification schemes")
def list_schemes(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items, total = crud.list_schemes(db, limit=limit, offset=offset)
    return schemas.Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/{scheme_id}", response_model=schemas.ClassificationSchemeRead, summary="Get a classification scheme")
def get_scheme(scheme_id: str, db: Session = Depends(get_db)):
    obj = crud.get_scheme(db, scheme_id)
    if obj is None:
        raise HTTPException(404, f"classification scheme '{scheme_id}' not found")
    return obj


@router.get(
    "/{scheme_id}/values",
    response_model=schemas.Page[schemas.ClassificationValueRead],
    summary="List the values that belong to a classification scheme",
)
def list_scheme_values(
    scheme_id: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    if crud.get_scheme(db, scheme_id) is None:
        raise HTTPException(404, f"classification scheme '{scheme_id}' not found")
    items, total = crud.list_scheme_values(db, scheme_id, limit=limit, offset=offset)
    return schemas.Page(items=items, total=total, limit=limit, offset=offset)


@router.post(
    "", response_model=schemas.ClassificationSchemeRead, status_code=201, summary="Create a classification scheme"
)
def create_scheme(data: schemas.ClassificationSchemeCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_scheme(db, data)
    except crud.ConflictError as exc:
        raise HTTPException(409, str(exc))


@router.put("/{scheme_id}", response_model=schemas.ClassificationSchemeRead, summary="Update a classification scheme")
def update_scheme(scheme_id: str, data: schemas.ClassificationSchemeUpdate, db: Session = Depends(get_db)):
    try:
        obj = crud.update_scheme(db, scheme_id, data)
    except crud.ConflictError as exc:
        raise HTTPException(409, str(exc))
    if obj is None:
        raise HTTPException(404, f"classification scheme '{scheme_id}' not found")
    return obj


@router.delete("/{scheme_id}", status_code=204, summary="Delete a classification scheme")
def delete_scheme(scheme_id: str, db: Session = Depends(get_db)):
    try:
        ok = crud.delete_scheme(db, scheme_id)
    except crud.ConflictError as exc:
        raise HTTPException(409, str(exc))
    if ok is None:
        raise HTTPException(404, f"classification scheme '{scheme_id}' not found")
    return None
