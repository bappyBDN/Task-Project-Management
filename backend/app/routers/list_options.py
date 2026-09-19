from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

router = APIRouter(prefix="/list-options", tags=["list-options"])

KINDS = ["category", "task_type", "priority", "status", "delay_category", "meeting_type"]


@router.get("")
def list_options(kind: str, db: Session = Depends(get_db)):
    rows = db.query(models.ListOption).filter(
        models.ListOption.kind == kind, models.ListOption.is_active.is_(True)
    ).order_by(models.ListOption.value).all()
    return [r.value for r in rows]


@router.post("", status_code=201)
def add_option(kind: str, value: str, db: Session = Depends(get_db)):
    kind = kind.strip().lower()
    value = value.strip()
    if not value:
        raise HTTPException(400, "Value is required")
    existing = db.query(models.ListOption).filter(
        models.ListOption.kind == kind, models.ListOption.value == value
    ).first()
    if existing:
        if not existing.is_active:
            existing.is_active = True
            db.commit()
        return {"kind": kind, "value": value}
    db.add(models.ListOption(kind=kind, value=value))
    db.commit()
    return {"kind": kind, "value": value}


@router.delete("", status_code=204)
def remove_option(kind: str, value: str, db: Session = Depends(get_db)):
    kind = kind.strip().lower()
    value = value.strip()
    row = db.query(models.ListOption).filter(
        models.ListOption.kind == kind, models.ListOption.value == value
    ).first()
    if row:
        row.is_active = False
        db.commit()
