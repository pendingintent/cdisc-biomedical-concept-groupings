from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/classification-values", tags=["Classification Values"])


@router.get(
    "",
    response_model=schemas.Page[schemas.ClassificationValueRead],
    summary="List classification values",
)
def list_values(
    scheme_id: Optional[str] = None,
    label_contains: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items, total = crud.list_values(
        db,
        scheme_id=scheme_id,
        label_contains=label_contains,
        limit=limit,
        offset=offset,
    )
    return schemas.Page(items=items, total=total, limit=limit, offset=offset)


@router.get(
    "/{value_id}",
    response_model=schemas.ClassificationValueRead,
    summary="Get a classification value",
)
def get_value(value_id: str, db: Session = Depends(get_db)):
    obj = crud.get_value(db, value_id)
    if obj is None:
        raise HTTPException(404, f"classification value '{value_id}' not found")
    return obj


@router.get(
    "/{value_id}/biomedical-concepts",
    response_model=schemas.ValueBiomedicalConcepts,
    summary="Get all biomedical concepts tagged with this classification value",
)
def get_value_biomedical_concepts(value_id: str, db: Session = Depends(get_db)):
    value = crud.get_value_biomedical_concepts(db, value_id)
    if value is None:
        raise HTTPException(404, f"classification value '{value_id}' not found")

    bcs = []
    seen = set()
    for assignment in value.assignments:
        if assignment.bc_id not in seen:
            seen.add(assignment.bc_id)
            bcs.append(assignment.biomedical_concept)

    return schemas.ValueBiomedicalConcepts(value=value, biomedical_concepts=bcs)


@router.post(
    "",
    response_model=schemas.ClassificationValueRead,
    status_code=201,
    summary="Create a classification value",
)
def create_value(
    data: schemas.ClassificationValueCreate, db: Session = Depends(get_db)
):
    try:
        return crud.create_value(db, data)
    except crud.ConflictError as exc:
        raise HTTPException(409, str(exc))


@router.put(
    "/{value_id}",
    response_model=schemas.ClassificationValueRead,
    summary="Update a classification value",
)
def update_value(
    value_id: str,
    data: schemas.ClassificationValueUpdate,
    db: Session = Depends(get_db),
):
    try:
        obj = crud.update_value(db, value_id, data)
    except crud.ConflictError as exc:
        raise HTTPException(409, str(exc))
    if obj is None:
        raise HTTPException(404, f"classification value '{value_id}' not found")
    return obj


@router.delete("/{value_id}", status_code=204, summary="Delete a classification value")
def delete_value(value_id: str, db: Session = Depends(get_db)):
    try:
        ok = crud.delete_value(db, value_id)
    except crud.ConflictError as exc:
        raise HTTPException(409, str(exc))
    if ok is None:
        raise HTTPException(404, f"classification value '{value_id}' not found")
    return None
