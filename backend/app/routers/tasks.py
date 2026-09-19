from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.auth import get_admin_user, get_current_user
from app.database import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[schemas.TaskOut])
def list_tasks(
    project_id: int | None = None,
    responsible_id: int | None = None,
    accountable_id: int | None = None,
    status: str | None = None,
    priority: str | None = None,
    health: str | None = None,
    overdue: bool | None = None,
    blocker: bool | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Task).filter(models.Task.is_deleted.is_(False))
    if project_id:
        q = q.filter(models.Task.project_id == project_id)
    if responsible_id:
        q = q.filter(models.Task.responsible_id == responsible_id)
    if accountable_id:
        q = q.filter(models.Task.accountable_id == accountable_id)
    if status:
        q = q.filter(models.Task.status == status)
    if priority:
        q = q.filter(models.Task.priority == priority)
    if health:
        q = q.filter(models.Task.health == health)
    if blocker is not None:
        q = q.filter(models.Task.blocker == blocker)
    if overdue is True:
        today = date.today()
        q = q.filter(
            models.Task.status.notin_(["completed", "closed", "cancelled"]),
            models.Task.approved_due_date.isnot(None),
            models.Task.approved_due_date < today,
        )
    return q.order_by(models.Task.approved_due_date, models.Task.priority).all()


@router.post("", response_model=schemas.TaskOut, status_code=201)
def create_task(payload: schemas.TaskBase, db: Session = Depends(get_db)):
    code = payload.code or services.next_code("TSK", db, models.Task)
    data = {**payload.model_dump(), "code": code}
    task = models.Task(**data)
    if task.status == "in_progress":
        task.status = "in_progress"
    db.add(task)
    db.flush()
    services.recalc_task_health(db, task)
    if task.project_id:
        services.recalc_project_health(db, task.project_id)
    services.audit(db, "system", "task", task.id, "created", new_value=task.title)
    services.notify(db, task.responsible_id, f"Task assigned: {task.title}",
                    body=f"You are responsible for {task.code}.", kind="assignment")
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task or task.is_deleted:
        raise HTTPException(404, "Task not found")
    return task


@router.patch("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, payload: schemas.TaskBase, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task or task.is_deleted:
        raise HTTPException(404, "Task not found")
    previous = task.title
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    services.recalc_task_health(db, task)
    if task.project_id:
        services.recalc_project_health(db, task.project_id)
    services.audit(db, "system", "task", task.id, "updated", previous_value=previous, new_value=task.title)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    task.is_deleted = True
    services.audit(db, "system", "task", task.id, "deleted", previous_value=task.title)
    db.commit()


@router.delete("/{task_id}/permanent", status_code=204)
def permanent_delete_task(task_id: int, admin: models.User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Admin-only: hard-delete a task (any user's) and its dependents."""
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    title = task.title
    # Remove dependent records first (FK safety)
    db.query(models.TaskDependency).filter(
        (models.TaskDependency.task_id == task_id) | (models.TaskDependency.depends_on_task_id == task_id)
    ).delete(synchronize_session=False)
    db.query(models.RaciEntry).filter(models.RaciEntry.task_id == task_id).delete(synchronize_session=False)
    db.query(models.ProgressUpdate).filter(models.ProgressUpdate.task_id == task_id).delete(synchronize_session=False)
    db.query(models.DelayRca).filter(models.DelayRca.task_id == task_id).delete(synchronize_session=False)
    db.query(models.Approval).filter(
        models.Approval.entity_type == "task", models.Approval.entity_id == task_id
    ).delete(synchronize_session=False)
    services.audit(db, admin.name, "task", task_id, "permanent_deleted", previous_value=title,
                   reason=f"Hard-deleted by admin {admin.name}")
    db.delete(task)
    db.commit()


# ---------------------------------------------------------------- Progress
@router.post("/{task_id}/progress", response_model=schemas.ProgressUpdateOut, status_code=201)
def add_progress(task_id: int, payload: schemas.ProgressUpdateBase, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    update = models.ProgressUpdate(**{**payload.model_dump(), "task_id": task_id})
    task.progress_pct = payload.progress_pct
    if payload.status:
        task.status = payload.status
    if payload.blocker:
        task.blocker = True
        task.blocker_details = payload.blocker_details or task.blocker_details
    if payload.forecast_due_date:
        task.forecast_due_date = payload.forecast_due_date
    services.recalc_task_health(db, task)
    if task.project_id:
        services.recalc_project_health(db, task.project_id)
    db.add(update)
    services.audit(db, "system", "task", task.id, "progress_updated", new_value=str(payload.progress_pct))
    db.commit()
    db.refresh(update)
    return update


@router.get("/{task_id}/progress", response_model=list[schemas.ProgressUpdateOut])
def list_progress(task_id: int, db: Session = Depends(get_db)):
    return db.query(models.ProgressUpdate).filter(models.ProgressUpdate.task_id == task_id).order_by(models.ProgressUpdate.created_at.desc()).all()
