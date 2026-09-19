from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.auth import get_admin_user
from app.database import get_db

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[schemas.ProjectOut])
def list_projects(
    company_id: int | None = None,
    function_id: int | None = None,
    status: str | None = None,
    health: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Project)
    if company_id:
        q = q.filter(models.Project.company_id == company_id)
    if function_id:
        q = q.filter(models.Project.function_id == function_id)
    if status:
        q = q.filter(models.Project.status == status)
    if health:
        q = q.filter(models.Project.health == health)
    return q.order_by(models.Project.name).all()


@router.post("", response_model=schemas.ProjectOut, status_code=201)
def create_project(payload: schemas.ProjectBase, db: Session = Depends(get_db)):
    code = payload.code or services.next_code("PRJ", db, models.Project)
    project = models.Project(**{**payload.model_dump(), "code": code})
    db.add(project)
    db.commit()
    db.refresh(project)
    services.audit(db, "system", "project", project.id, "created", new_value=project.name)
    db.commit()
    return project


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.patch("/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, payload: schemas.ProjectBase, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(project, k, v)
    services.audit(db, "system", "project", project.id, "updated", new_value=project.name)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}/milestones", response_model=list[schemas.MilestoneOut])
def list_milestones(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.Milestone).filter(models.Milestone.project_id == project_id).order_by(models.Milestone.due_date).all()


@router.post("/{project_id}/milestones", response_model=schemas.MilestoneOut, status_code=201)
def create_milestone(project_id: int, payload: schemas.MilestoneBase, db: Session = Depends(get_db)):
    ms = models.Milestone(**{**payload.model_dump(), "project_id": project_id})
    db.add(ms)
    db.commit()
    db.refresh(ms)
    return ms


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, admin: models.User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Admin-only: delete a project and its milestones/tasks (soft-delete tasks, hard-delete project)."""
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    name = project.name
    # Soft-delete tasks so history is preserved
    tasks = db.query(models.Task).filter(models.Task.project_id == project_id).all()
    for t in tasks:
        t.is_deleted = True
    db.query(models.Milestone).filter(models.Milestone.project_id == project_id).delete(synchronize_session=False)
    db.query(models.BacklogItem).filter(models.BacklogItem.project_id == project_id).update(
        {"project_id": None}, synchronize_session=False)
    db.query(models.RaciEntry).filter(models.RaciEntry.project_id == project_id).delete(synchronize_session=False)
    services.audit(db, admin.name, "project", project_id, "deleted", previous_value=name,
                   reason=f"Deleted by admin {admin.name}")
    db.delete(project)
    db.commit()
