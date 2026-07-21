import uuid
from typing import Optional, Sequence, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas


class ConflictError(Exception):
    """Raised for FK/unique-constraint violations that should surface as HTTP 409."""


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _commit_or_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(str(exc.orig)) from exc


def _paginate(query, limit: int, offset: int) -> Tuple[Sequence, int]:
    total = query.order_by(None).count()
    items = query.limit(limit).offset(offset).all()
    return items, total


# --- Biomedical Concept ---


def list_biomedical_concepts(
    db: Session,
    ncit_code: Optional[str] = None,
    short_name_contains: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    query = db.query(models.BiomedicalConcept)
    if ncit_code:
        query = query.filter(models.BiomedicalConcept.ncit_code == ncit_code)
    if short_name_contains:
        query = query.filter(
            models.BiomedicalConcept.short_name.ilike(f"%{_escape_like(short_name_contains)}%", escape="\\")
        )
    query = query.order_by(models.BiomedicalConcept.bc_id)
    return _paginate(query, limit, offset)


def get_biomedical_concept(db: Session, bc_id: str) -> Optional[models.BiomedicalConcept]:
    return db.get(models.BiomedicalConcept, bc_id)


def create_biomedical_concept(db: Session, data: schemas.BiomedicalConceptCreate) -> models.BiomedicalConcept:
    if get_biomedical_concept(db, data.bc_id) is not None:
        raise ConflictError(f"biomedical_concept '{data.bc_id}' already exists")
    obj = models.BiomedicalConcept(**data.model_dump())
    db.add(obj)
    _commit_or_conflict(db)
    db.refresh(obj)
    return obj


def update_biomedical_concept(
    db: Session, bc_id: str, data: schemas.BiomedicalConceptUpdate
) -> Optional[models.BiomedicalConcept]:
    obj = get_biomedical_concept(db, bc_id)
    if obj is None:
        return None
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    _commit_or_conflict(db)
    db.refresh(obj)
    return obj


def delete_biomedical_concept(db: Session, bc_id: str) -> Optional[bool]:
    obj = get_biomedical_concept(db, bc_id)
    if obj is None:
        return None
    if db.query(models.BCClassificationAssignment).filter_by(bc_id=bc_id).first() is not None:
        raise ConflictError(
            f"Cannot delete biomedical_concept '{bc_id}': it is referenced by existing classification assignments"
        )
    db.delete(obj)
    _commit_or_conflict(db)
    return True


def get_biomedical_concept_classifications(db: Session, bc_id: str) -> Optional[models.BiomedicalConcept]:
    return get_biomedical_concept(db, bc_id)


# --- Classification Scheme ---


def list_schemes(db: Session, limit: int = 50, offset: int = 0):
    query = db.query(models.BCClassificationScheme).order_by(models.BCClassificationScheme.scheme_id)
    return _paginate(query, limit, offset)


def get_scheme(db: Session, scheme_id: str) -> Optional[models.BCClassificationScheme]:
    return db.get(models.BCClassificationScheme, scheme_id)


def create_scheme(db: Session, data: schemas.ClassificationSchemeCreate) -> models.BCClassificationScheme:
    if get_scheme(db, data.scheme_id) is not None:
        raise ConflictError(f"bc_classification_scheme '{data.scheme_id}' already exists")
    obj = models.BCClassificationScheme(**data.model_dump())
    db.add(obj)
    _commit_or_conflict(db)
    db.refresh(obj)
    return obj


def update_scheme(
    db: Session, scheme_id: str, data: schemas.ClassificationSchemeUpdate
) -> Optional[models.BCClassificationScheme]:
    obj = get_scheme(db, scheme_id)
    if obj is None:
        return None
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    _commit_or_conflict(db)
    db.refresh(obj)
    return obj


def delete_scheme(db: Session, scheme_id: str) -> Optional[bool]:
    obj = get_scheme(db, scheme_id)
    if obj is None:
        return None
    if db.query(models.BCClassificationValue).filter_by(scheme_id=scheme_id).first() is not None:
        raise ConflictError(f"Cannot delete scheme '{scheme_id}': it still has classification values")
    if db.query(models.BCClassificationAssignment).filter_by(scheme_id=scheme_id).first() is not None:
        raise ConflictError(f"Cannot delete scheme '{scheme_id}': it is referenced by existing classification assignments")
    db.delete(obj)
    _commit_or_conflict(db)
    return True


def list_scheme_values(db: Session, scheme_id: str, limit: int = 50, offset: int = 0):
    query = (
        db.query(models.BCClassificationValue)
        .filter_by(scheme_id=scheme_id)
        .order_by(models.BCClassificationValue.value_id)
    )
    return _paginate(query, limit, offset)


# --- Classification Value ---


def list_values(
    db: Session,
    scheme_id: Optional[str] = None,
    label_contains: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    query = db.query(models.BCClassificationValue)
    if scheme_id:
        query = query.filter(models.BCClassificationValue.scheme_id == scheme_id)
    if label_contains:
        query = query.filter(
            models.BCClassificationValue.label.ilike(f"%{_escape_like(label_contains)}%", escape="\\")
        )
    query = query.order_by(models.BCClassificationValue.value_id)
    return _paginate(query, limit, offset)


def get_value(db: Session, value_id: str) -> Optional[models.BCClassificationValue]:
    return db.get(models.BCClassificationValue, value_id)


def create_value(db: Session, data: schemas.ClassificationValueCreate) -> models.BCClassificationValue:
    if get_value(db, data.value_id) is not None:
        raise ConflictError(f"bc_classification_value '{data.value_id}' already exists")
    if get_scheme(db, data.scheme_id) is None:
        raise ConflictError(f"scheme '{data.scheme_id}' does not exist")
    obj = models.BCClassificationValue(**data.model_dump())
    db.add(obj)
    _commit_or_conflict(db)
    db.refresh(obj)
    return obj


def update_value(
    db: Session, value_id: str, data: schemas.ClassificationValueUpdate
) -> Optional[models.BCClassificationValue]:
    obj = get_value(db, value_id)
    if obj is None:
        return None
    if get_scheme(db, data.scheme_id) is None:
        raise ConflictError(f"scheme '{data.scheme_id}' does not exist")
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    _commit_or_conflict(db)
    db.refresh(obj)
    return obj


def delete_value(db: Session, value_id: str) -> Optional[bool]:
    obj = get_value(db, value_id)
    if obj is None:
        return None
    if db.query(models.BCClassificationAssignment).filter_by(value_id=value_id).first() is not None:
        raise ConflictError(f"Cannot delete value '{value_id}': it is referenced by existing classification assignments")
    db.delete(obj)
    _commit_or_conflict(db)
    return True


def get_value_biomedical_concepts(db: Session, value_id: str) -> Optional[models.BCClassificationValue]:
    return get_value(db, value_id)


# --- Classification Assignment ---


def list_assignments(
    db: Session,
    bc_id: Optional[str] = None,
    scheme_id: Optional[str] = None,
    value_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    query = db.query(models.BCClassificationAssignment)
    if bc_id:
        query = query.filter(models.BCClassificationAssignment.bc_id == bc_id)
    if scheme_id:
        query = query.filter(models.BCClassificationAssignment.scheme_id == scheme_id)
    if value_id:
        query = query.filter(models.BCClassificationAssignment.value_id == value_id)
    query = query.order_by(models.BCClassificationAssignment.assignment_id)
    return _paginate(query, limit, offset)


def get_assignment(db: Session, assignment_id: str) -> Optional[models.BCClassificationAssignment]:
    return db.get(models.BCClassificationAssignment, assignment_id)


def _validate_assignment_references(db: Session, bc_id: str, scheme_id: str, value_id: str) -> None:
    if get_biomedical_concept(db, bc_id) is None:
        raise ConflictError(f"biomedical_concept '{bc_id}' does not exist")
    value = get_value(db, value_id)
    if value is None or value.scheme_id != scheme_id:
        raise ConflictError(f"classification value '{value_id}' does not exist in scheme '{scheme_id}'")


def create_assignment(db: Session, data: schemas.ClassificationAssignmentCreate) -> models.BCClassificationAssignment:
    _validate_assignment_references(db, data.bc_id, data.scheme_id, data.value_id)
    if (
        db.query(models.BCClassificationAssignment)
        .filter_by(bc_id=data.bc_id, scheme_id=data.scheme_id, value_id=data.value_id)
        .first()
        is not None
    ):
        raise ConflictError("This biomedical_concept is already assigned this classification value")
    obj = models.BCClassificationAssignment(assignment_id=f"tag_{uuid.uuid4().hex}", **data.model_dump())
    db.add(obj)
    _commit_or_conflict(db)
    db.refresh(obj)
    return obj


def update_assignment(
    db: Session, assignment_id: str, data: schemas.ClassificationAssignmentUpdate
) -> Optional[models.BCClassificationAssignment]:
    obj = get_assignment(db, assignment_id)
    if obj is None:
        return None
    _validate_assignment_references(db, data.bc_id, data.scheme_id, data.value_id)
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    _commit_or_conflict(db)
    db.refresh(obj)
    return obj


def delete_assignment(db: Session, assignment_id: str) -> Optional[bool]:
    obj = get_assignment(db, assignment_id)
    if obj is None:
        return None
    db.delete(obj)
    _commit_or_conflict(db)
    return True
