from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/classification-assignments", tags=["Classification Assignments"])


@router.get(
    "", response_model=schemas.Page[schemas.ClassificationAssignmentRead], summary="List classification assignments"
)
def list_assignments(
    bc_id: Optional[str] = None,
    scheme_id: Optional[str] = None,
    value_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items, total = crud.list_assignments(
        db, bc_id=bc_id, scheme_id=scheme_id, value_id=value_id, limit=limit, offset=offset
    )
    return schemas.Page(items=items, total=total, limit=limit, offset=offset)


@router.get(
    "/{assignment_id}", response_model=schemas.ClassificationAssignmentRead, summary="Get a classification assignment"
)
def get_assignment(assignment_id: str, db: Session = Depends(get_db)):
    obj = crud.get_assignment(db, assignment_id)
    if obj is None:
        raise HTTPException(404, f"classification assignment '{assignment_id}' not found")
    return obj


@router.post(
    "",
    response_model=schemas.ClassificationAssignmentRead,
    status_code=201,
    summary="Create a classification assignment (tags a biomedical concept with a classification value)",
)
def create_assignment(data: schemas.ClassificationAssignmentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_assignment(db, data)
    except crud.ConflictError as exc:
        raise HTTPException(409, str(exc))


@router.put(
    "/{assignment_id}", response_model=schemas.ClassificationAssignmentRead, summary="Update a classification assignment"
)
def update_assignment(assignment_id: str, data: schemas.ClassificationAssignmentUpdate, db: Session = Depends(get_db)):
    try:
        obj = crud.update_assignment(db, assignment_id, data)
    except crud.ConflictError as exc:
        raise HTTPException(409, str(exc))
    if obj is None:
        raise HTTPException(404, f"classification assignment '{assignment_id}' not found")
    return obj


@router.delete("/{assignment_id}", status_code=204, summary="Delete a classification assignment")
def delete_assignment(assignment_id: str, db: Session = Depends(get_db)):
    ok = crud.delete_assignment(db, assignment_id)
    if ok is None:
        raise HTTPException(404, f"classification assignment '{assignment_id}' not found")
    return None
