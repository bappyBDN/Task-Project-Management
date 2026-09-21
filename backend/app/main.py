from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app import auth, models
from app.config import settings
from app.database import SessionLocal, engine, get_db
from app.routers import (
    approvals,
    audit,
    backlogs,
    dashboards,
    delays,
    email_notifications,
    governance,
    list_options,
    organizations,
    privileged,
    projects,
    raci,
    tasks,
    user_mapping,
)
from app.scheduler import start_scheduler, stop_scheduler
from app.seed import seed

# Database tables creation
models.Base.metadata.create_all(bind=engine)

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

# CORS Setup for Vercel and Localhost
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://task-project-management-ten.vercel.app",
    "https://task-project-management-git-main-abc-8e17.vercel.app",
    "https://task-project-management-728ktac08-abc-8e17.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://task-project-management-ten.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # যেকোনো .vercel.app ডোমেইন এলাউ করবে
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# List of all routers
routers = [
    auth.router,
    organizations.router,
    projects.router,
    tasks.router,
    delays.router,
    approvals.router,
    backlogs.router,
    dashboards.router,
    audit.router,
    governance.router,
    raci.router,
    privileged.router,
    list_options.router,
    email_notifications.router,
    user_mapping.router,
]

# Register routers with and without /api prefix to ensure Vercel frontend works seamlessly
for r in routers:
    app.include_router(r, prefix="/api")
    app.include_router(r)


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
@app.get("/api/email-logs")
def get_email_logs(db: Session = Depends(get_db)):
    logs = (
        db.query(models.EmailLog)
        .order_by(models.EmailLog.sent_date.desc())
        .limit(200)
        .all()
    )
    result = []
    for log in logs:
        result.append(
            {
                "id": log.id,
                "task_id": log.entity_id if log.entity_type == "task" else None,
                "backlog_item_id": (
                    log.entity_id if log.entity_type == "backlog" else None
                ),
                "email_type": log.email_type,
                "sent_at": str(log.sent_date),
            }
        )
    return result


@app.get("/")
def root():
    return {"app": settings.app_name, "docs": "/docs"}
