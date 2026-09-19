from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.auth import get_admin_user, get_current_user
from app.database import get_db

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/companies", response_model=list[schemas.CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return db.query(models.Company).order_by(models.Company.name).all()


@router.post("/companies", response_model=schemas.CompanyOut, status_code=201)
def create_company(payload: schemas.CompanyBase, db: Session = Depends(get_db)):
    company = models.Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/functions", response_model=list[schemas.FunctionOut])
def list_functions(db: Session = Depends(get_db)):
    return db.query(models.Function).order_by(models.Function.name).all()


@router.post("/functions", response_model=schemas.FunctionOut, status_code=201)
def create_function(payload: schemas.FunctionBase, db: Session = Depends(get_db)):
    fn = models.Function(**payload.model_dump())
    db.add(fn)
    db.commit()
    db.refresh(fn)
    return fn


@router.get("/users", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).order_by(models.User.name).all()


@router.get("/users/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user


@router.post("/users", response_model=schemas.UserOut, status_code=201)
def create_user(payload: schemas.UserBase, admin: models.User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = models.User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, payload: schemas.UserBase, admin: models.User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def deactivate_user(user_id: int, admin: models.User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.is_active = False
    db.commit()


@router.delete("/users/{user_id}/permanent", status_code=204)
def permanent_delete_user(user_id: int, admin: models.User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Admin-only: hard-delete a user after clearing their references."""
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if user.role == "admin":
        raise HTTPException(400, "Cannot delete an admin account")

    # Null out FKs referencing this user
    for model, cols in [
        (models.Project, ["sponsor_id", "manager_id", "owner_id"]),
        (models.Task, ["responsible_id", "accountable_id", "reviewer_id"]),
        (models.DelayRca, ["recovery_owner_id"]),
        (models.BacklogItem, ["requested_by_id"]),
        (models.Approval, ["requested_by_id", "approver_id"]),
        (models.Decision, ["owner_id"]),
        (models.ManagementAction, ["responsible_id", "accountable_id"]),
        (models.Risk, ["owner_id"]),
        (models.Issue, ["owner_id"]),
    ]:
        db.query(model).filter(getattr(model, cols[0]) == user_id).update({cols[0]: None}, synchronize_session=False)
        for col in cols[1:]:
            db.query(model).filter(getattr(model, col) == user_id).update({col: None}, synchronize_session=False)

    db.query(models.RaciEntry).filter(models.RaciEntry.user_id == user_id).delete(synchronize_session=False)
    db.query(models.Notification).filter(models.Notification.user_id == user_id).delete(synchronize_session=False)

    db.delete(user)
    db.commit()
