from typing import List, Optional

from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BiomedicalConcept(Base):
    __tablename__ = "biomedical_concept"

    bc_id: Mapped[str] = mapped_column(primary_key=True)
    short_name: Mapped[str]
    ncit_code: Mapped[Optional[str]]

    assignments: Mapped[List["BCClassificationAssignment"]] = relationship(
        back_populates="biomedical_concept"
    )


class BCClassificationScheme(Base):
    __tablename__ = "bc_classification_scheme"

    scheme_id: Mapped[str] = mapped_column(primary_key=True)
    scheme_prefix: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    purpose: Mapped[str]
    intended_use: Mapped[str]

    values: Mapped[List["BCClassificationValue"]] = relationship(back_populates="scheme")


class BCClassificationValue(Base):
    __tablename__ = "bc_classification_value"
    __table_args__ = (
        UniqueConstraint("scheme_id", "label"),
        UniqueConstraint("value_id", "scheme_id"),
    )

    value_id: Mapped[str] = mapped_column(primary_key=True)
    scheme_id: Mapped[str] = mapped_column(ForeignKey("bc_classification_scheme.scheme_id"))
    label: Mapped[str]
    description: Mapped[str]

    scheme: Mapped["BCClassificationScheme"] = relationship(back_populates="values")
    assignments: Mapped[List["BCClassificationAssignment"]] = relationship(back_populates="value")


class BCClassificationAssignment(Base):
    __tablename__ = "bc_classification_assignment"
    __table_args__ = (
        UniqueConstraint("bc_id", "scheme_id", "value_id"),
        ForeignKeyConstraint(
            ["value_id", "scheme_id"],
            ["bc_classification_value.value_id", "bc_classification_value.scheme_id"],
        ),
    )

    assignment_id: Mapped[str] = mapped_column(primary_key=True)
    bc_id: Mapped[str] = mapped_column(ForeignKey("biomedical_concept.bc_id"))
    scheme_id: Mapped[str] = mapped_column()
    value_id: Mapped[str] = mapped_column()

    biomedical_concept: Mapped["BiomedicalConcept"] = relationship(back_populates="assignments")
    value: Mapped["BCClassificationValue"] = relationship(back_populates="assignments")
