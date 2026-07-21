from fastapi import FastAPI

from app.routers import (
    biomedical_concepts,
    classification_assignments,
    classification_schemes,
    classification_values,
)

app = FastAPI(
    title="Biomedical Concept Grouping API",
    description=(
        "Read/write access to the bc_grouping.db SQLite database: biomedical concepts, "
        "their classification schemes/values, and the assignments linking BCs to those values. "
        "See bc-classification-grouping.md for the underlying ER diagram."
    ),
    version="0.1.0",
)

app.include_router(biomedical_concepts.router)
app.include_router(classification_schemes.router)
app.include_router(classification_values.router)
app.include_router(classification_assignments.router)


@app.get("/health", tags=["Health"], summary="Liveness check")
def health():
    return {"status": "ok"}
