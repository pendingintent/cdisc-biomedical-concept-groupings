from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/biomedical-concepts", tags=["Biomedical Concepts"])


@router.get("", response_model=schemas.Page[schemas.BiomedicalConceptRead], summary="List biomedical concepts")
def list_biomedical_concepts(
    ncit_code: Optional[str] = None,
    short_name_contains: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items, total = crud.list_biomedical_concepts(
        db, ncit_code=ncit_code, short_name_contains=short_name_contains, limit=limit, offset=offset
    )
    return schemas.Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/{bc_id}", response_model=schemas.BiomedicalConceptRead, summary="Get a biomedical concept")
def get_biomedical_concept(bc_id: str, db: Session = Depends(get_db)):
    obj = crud.get_biomedical_concept(db, bc_id)
    if obj is None:
        raise HTTPException(404, f"biomedical_concept '{bc_id}' not found")
    return obj


@router.get(
    "/{bc_id}/classifications",
    response_model=schemas.BiomedicalConceptClassifications,
    summary="Get all classifications for a biomedical concept, grouped by scheme",
)
def get_biomedical_concept_classifications(bc_id: str, db: Session = Depends(get_db)):
    bc = crud.get_biomedical_concept_classifications(db, bc_id)
    if bc is None:
        raise HTTPException(404, f"biomedical_concept '{bc_id}' not found")

    groups: dict = {}
    order: list = []
    for assignment in bc.assignments:
        value = assignment.value
        scheme = value.scheme
        if scheme.scheme_id not in groups:
            groups[scheme.scheme_id] = {"scheme": scheme, "values": []}
            order.append(scheme.scheme_id)
        if value not in groups[scheme.scheme_id]["values"]:
            groups[scheme.scheme_id]["values"].append(value)

    classifications = [
        schemas.SchemeClassificationGroup(scheme=groups[sid]["scheme"], values=groups[sid]["values"])
        for sid in order
    ]
    return schemas.BiomedicalConceptClassifications(biomedical_concept=bc, classifications=classifications)


@router.post("", response_model=schemas.BiomedicalConceptRead, status_code=201, summary="Create a biomedical concept")
def create_biomedical_concept(data: schemas.BiomedicalConceptCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_biomedical_concept(db, data)
    except crud.ConflictError as exc:
        raise HTTPException(409, str(exc))


@router.put("/{bc_id}", response_model=schemas.BiomedicalConceptRead, summary="Update a biomedical concept")
def update_biomedical_concept(bc_id: str, data: schemas.BiomedicalConceptUpdate, db: Session = Depends(get_db)):
    try:
        obj = crud.update_biomedical_concept(db, bc_id, data)
    except crud.ConflictError as exc:
        raise HTTPException(409, str(exc))
    if obj is None:
        raise HTTPException(404, f"biomedical_concept '{bc_id}' not found")
    return obj


@router.delete("/{bc_id}", status_code=204, summary="Delete a biomedical concept")
def delete_biomedical_concept(bc_id: str, db: Session = Depends(get_db)):
    try:
        ok = crud.delete_biomedical_concept(db, bc_id)
    except crud.ConflictError as exc:
        raise HTTPException(409, str(exc))
    if ok is None:
        raise HTTPException(404, f"biomedical_concept '{bc_id}' not found")
    return None
