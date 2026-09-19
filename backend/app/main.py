from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.config import settings
from app.database import engine, SessionLocal
from app.routers import organizations, projects, tasks, delays, approvals, backlogs, dashboards, audit, governance, raci, list_options
from app.seed import seed

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(list_options.router)


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"app": settings.app_name, "docs": "/docs"}
