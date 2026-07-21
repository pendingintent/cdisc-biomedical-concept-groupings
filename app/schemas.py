from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int


# --- Biomedical Concept ---


class BiomedicalConceptBase(BaseModel):
    short_name: str
    ncit_code: Optional[str] = None


class BiomedicalConceptCreate(BiomedicalConceptBase):
    bc_id: str


class BiomedicalConceptUpdate(BiomedicalConceptBase):
    pass


class BiomedicalConceptRead(BiomedicalConceptBase):
    model_config = ConfigDict(from_attributes=True)

    bc_id: str


# --- Classification Scheme ---


class ClassificationSchemeBase(BaseModel):
    scheme_prefix: str
    name: str
    description: str
    purpose: str
    intended_use: str


class ClassificationSchemeCreate(ClassificationSchemeBase):
    scheme_id: str


class ClassificationSchemeUpdate(ClassificationSchemeBase):
    pass


class ClassificationSchemeRead(ClassificationSchemeBase):
    model_config = ConfigDict(from_attributes=True)

    scheme_id: str


# --- Classification Value ---


class ClassificationValueBase(BaseModel):
    scheme_id: str
    label: str
    description: str


class ClassificationValueCreate(ClassificationValueBase):
    value_id: str


class ClassificationValueUpdate(ClassificationValueBase):
    pass


class ClassificationValueRead(ClassificationValueBase):
    model_config = ConfigDict(from_attributes=True)

    value_id: str


# --- Classification Assignment ---


class ClassificationAssignmentBase(BaseModel):
    bc_id: str
    scheme_id: str
    value_id: str


class ClassificationAssignmentCreate(ClassificationAssignmentBase):
    pass


class ClassificationAssignmentUpdate(ClassificationAssignmentBase):
    pass


class ClassificationAssignmentRead(ClassificationAssignmentBase):
    model_config = ConfigDict(from_attributes=True)

    assignment_id: str


# --- Composite / joined views ---


class SchemeClassificationGroup(BaseModel):
    scheme: ClassificationSchemeRead
    values: List[ClassificationValueRead]


class BiomedicalConceptClassifications(BaseModel):
    biomedical_concept: BiomedicalConceptRead
    classifications: List[SchemeClassificationGroup]


class ValueBiomedicalConcepts(BaseModel):
    value: ClassificationValueRead
    biomedical_concepts: List[BiomedicalConceptRead]
