from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.config import settings
from app.database import engine, SessionLocal
from app import auth  # 👈 login / forgot-password / reset-password
from app.routers import (
    organizations, projects, tasks, delays, approvals, backlogs, dashboards,
    audit, governance, raci, list_options, email_notifications, privileged, user_mapping,
)
from app.scheduler import start_scheduler, stop_scheduler
from app.seed import seed

models.Base.metadata.create_all(bind=engine)

# `create_all` creates missing TABLES but never adds new COLUMNS to tables that
# already exist. These ADD COLUMN statements patch older databases in place.
_NEW_COLUMNS = [
    ("tasks", "department_id", "INTEGER REFERENCES departments(id)"),
    ("users", "hashed_password", "VARCHAR(255)"),
    ("users", "reset_token", "VARCHAR(128)"),
    ("users", "reset_token_expires", "DATETIME"),
    ("users", "reports_to_id", "INTEGER REFERENCES users(id)"),
]


def ensure_columns():
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    with engine.begin() as conn:
        for table, column, ddl in _NEW_COLUMNS:
            if table in tables and column not in {
                c["name"] for c in insp.get_columns(table)
            }:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))


ensure_columns()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)          # 👈 mounts /auth/login, /auth/forgot-password, /auth/reset-password
app.include_router(organizations.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(delays.router)
app.include_router(approvals.router)
app.include_router(backlogs.router)
app.include_router(dashboards.router)
app.include_router(audit.router)
app.include_router(governance.router)
app.include_router(raci.router)
app.include_router(privileged.router)
app.include_router(list_options.router)
app.include_router(email_notifications.router)
app.include_router(user_mapping.router)


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    if settings.mail_enabled:
        start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()

@app.get("/email-logs")
def get_email_logs(db: Session = Depends(get_db)):
    logs = db.query(models.EmailLog).order_by(models.EmailLog.sent_date.desc()).limit(200).all()
    # ফ্রন্টএন্ডের সুবিধার জন্য ডাটা ম্যাপিং করে পাঠানো হলো
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "task_id": log.entity_id if log.entity_type == "task" else None,
            "backlog_item_id": log.entity_id if log.entity_type == "backlog" else None,
            "email_type": log.email_type,
            "sent_at": str(log.sent_date)
        })
    return result

@app.get("/")
def root():
    return {"app": settings.app_name, "docs": "/docs"}