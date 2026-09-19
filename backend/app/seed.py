"""Seed data for demo purposes. Idempotent — skips if data already exists."""
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app import models


def seed(db: Session):
    if db.query(models.Company).count() > 0:
        _ensure_admin(db)
        _ensure_list_options(db)
        return

    today = date.today()

    _seed_list_options(db)

    # Companies
    group = models.Company(name="Anwar Group", code="ANW", is_active=True)
    anwar_cement = models.Company(name="Anwar Cement", code="ACL", is_active=True)
    anwar_galv = models.Company(name="Anwar Galvanizing", code="AGL", is_active=True)
    db.add_all([group, anwar_cement, anwar_galv])

    # Functions
    fns = [
        models.Function(name="Operations", code="OPS"),
        models.Function(name="Finance", code="FIN"),
        models.Function(name="Sales & Marketing", code="S&M"),
        models.Function(name="IT & Digital", code="ITD"),
        models.Function(name="Supply Chain", code="SCM"),
        models.Function(name="HR", code="HR"),
    ]
    db.add_all(fns)
    db.flush()

    # Users
    users = [
        models.User(employee_id="E001", name="Rahim Uddin", email="rahim@anwargroup.com", designation="Group CEO", role="group_executive", company_id=group.id),
        models.User(employee_id="E002", name="Karim Ahmed", email="karim@anwarcement.com", designation="Business Head", role="business_head", company_id=anwar_cement.id, function_id=fns[0].id),
        models.User(employee_id="E003", name="Shahin Alam", email="shahin@anwargroup.com", designation="CFO", role="functional_head", function_id=fns[1].id),
        models.User(employee_id="E004", name="Farida Khan", email="farida@anwargroup.com", designation="PMO Lead", role="pmo"),
        models.User(employee_id="E005", name="Tanvir Hasan", email="tanvir@anwarcement.com", designation="Project Manager", role="pm", company_id=anwar_cement.id),
        models.User(employee_id="E006", name="Nusrat Jahan", email="nusrat@anwarcement.com", designation="Engineer", role="employee", company_id=anwar_cement.id, function_id=fns[0].id),
        models.User(employee_id="E007", name="Imran Kabir", email="imran@anwarcement.com", designation="Sales Lead", role="team_lead", company_id=anwar_cement.id, function_id=fns[2].id),
        models.User(employee_id="E008", name="Sadia Rahman", email="sadia@anwargroup.com", designation="Auditor", role="auditor", function_id=fns[1].id),
        models.User(employee_id="E009", name="System Administrator", email="admin@anwargroup.com", designation="Platform Admin", role="admin", company_id=group.id, function_id=fns[3].id),
    ]
    db.add_all(users)
    db.flush()

    # Program + Project
    program = models.Program(name="Operational Excellence 2026", company_id=anwar_cement.id)
    db.add(program)
    db.flush()

    p1 = models.Project(
        code="PRJ-0001", name="Cement Plant Digital Transformation",
        company_id=anwar_cement.id, function_id=fns[3].id, program_id=program.id,
        sponsor_id=users[1].id, manager_id=users[4].id, owner_id=users[4].id,
        strategic_objective="Digitalize plant operations to reduce cost and downtime.",
        objective="Implement IoT monitoring across the production line.",
        expected_outcome="15% reduction in unplanned downtime.",
        project_type="transformation", priority="high", methodology="hybrid",
        start_date=today - timedelta(days=60), baseline_due_date=today + timedelta(days=90),
        approved_due_date=today + timedelta(days=90), forecast_due_date=today + timedelta(days=105),
        completion_pct=40.0, status="active", health="amber", budget=12_000_000, criticality="high",
    )
    p2 = models.Project(
        code="PRJ-0002", name="Route-to-Market Expansion",
        company_id=anwar_cement.id, function_id=fns[2].id, program_id=program.id,
        sponsor_id=users[1].id, manager_id=users[6].id, owner_id=users[6].id,
        strategic_objective="Expand distribution footprint.",
        objective="Add 200 new retail points in 3 districts.",
        expected_outcome="12% revenue growth.",
        project_type="strategic", priority="high", methodology="kanban",
        start_date=today - timedelta(days=30), baseline_due_date=today + timedelta(days=180),
        approved_due_date=today + timedelta(days=180),
        completion_pct=25.0, status="active", health="green", budget=5_000_000, criticality="medium",
    )
    db.add_all([p1, p2])
    db.flush()

    ms1 = models.Milestone(project_id=p1.id, name="Sensor Installation", due_date=today + timedelta(days=30), status="in_progress", completion_pct=50.0)
    ms2 = models.Milestone(project_id=p1.id, name="Dashboard Go-Live", due_date=today + timedelta(days=90), status="not_started", completion_pct=0.0)
    db.add_all([ms1, ms2])
    db.flush()

    # Tasks
    tasks = [
        models.Task(code="TSK-0001", project_id=p1.id, milestone_id=ms1.id, company_id=anwar_cement.id, function_id=fns[3].id,
                    title="Install vibration sensors on Kiln 2", description="Mount and calibrate 40 sensors.",
                    expected_deliverable="Sensors streaming data to cloud.", category="digital_transformation", task_type="task",
                    priority="high", responsible_id=users[5].id, accountable_id=users[4].id, reviewer_id=users[4].id,
                    planned_start_date=today - timedelta(days=20), baseline_due_date=today + timedelta(days=10),
                    approved_due_date=today + timedelta(days=10), progress_pct=70.0, status="in_progress", health="green"),
        models.Task(code="TSK-0002", project_id=p1.id, milestone_id=ms1.id, company_id=anwar_cement.id, function_id=fns[3].id,
                    title="Provision cloud telemetry pipeline", description="Set up ingestion and storage.",
                    expected_deliverable="Working data pipeline.", category="digital_transformation", task_type="task",
                    priority="critical", responsible_id=users[5].id, accountable_id=users[4].id, reviewer_id=users[4].id,
                    planned_start_date=today - timedelta(days=40), baseline_due_date=today - timedelta(days=2),
                    approved_due_date=today - timedelta(days=2), progress_pct=55.0, status="in_progress", health="red",
                    blocker=True, blocker_details="Cloud vendor credential approval pending."),
        models.Task(code="TSK-0003", project_id=p1.id, company_id=anwar_cement.id, function_id=fns[3].id,
                    title="Train plant operators", description="Conduct IoT dashboard training.",
                    expected_deliverable="Trained operators (sign-off sheet).", category="digital_transformation", task_type="task",
                    priority="medium", responsible_id=users[6].id, accountable_id=users[4].id,
                    planned_start_date=today + timedelta(days=5), baseline_due_date=today + timedelta(days=60),
                    approved_due_date=today + timedelta(days=60), progress_pct=0.0, status="backlog", health="green"),
        models.Task(code="TSK-0004", project_id=p2.id, company_id=anwar_cement.id, function_id=fns[2].id,
                    title="Appoint 3 new distributors", description="Finalize distributor agreements.",
                    expected_deliverable="Signed agreements.", category="sales", task_type="task",
                    priority="high", responsible_id=users[6].id, accountable_id=users[1].id,
                    planned_start_date=today - timedelta(days=10), baseline_due_date=today + timedelta(days=20),
                    approved_due_date=today + timedelta(days=20), progress_pct=60.0, status="in_progress", health="green"),
        models.Task(code="TSK-0005", project_id=p2.id, company_id=anwar_cement.id, function_id=fns[2].id,
                    title="Retail coverage survey", description="Survey retail density in 3 districts.",
                    expected_deliverable="Survey report.", category="sales", task_type="task",
                    priority="medium", responsible_id=users[6].id, accountable_id=users[1].id,
                    planned_start_date=today - timedelta(days=5), baseline_due_date=today + timedelta(days=3),
                    approved_due_date=today + timedelta(days=3), progress_pct=30.0, status="in_progress", health="amber"),
    ]
    db.add_all(tasks)
    db.flush()

    # RACI
    db.add_all([
        models.RaciEntry(task_id=tasks[0].id, user_id=users[5].id, raci_type="R"),
        models.RaciEntry(task_id=tasks[0].id, user_id=users[4].id, raci_type="A"),
        models.RaciEntry(task_id=tasks[1].id, user_id=users[5].id, raci_type="R"),
        models.RaciEntry(task_id=tasks[1].id, user_id=users[4].id, raci_type="A"),
    ])

    # Delay / RCA on the overdue task
    db.add(models.DelayRca(
        task_id=tasks[1].id, delay_category="vendor_delay", delay_reason="Cloud credentials not issued.",
        root_cause="Procurement approval queue bottleneck.", is_internal=True, dependency_related=False,
        responsible_party="IT Procurement", business_impact="Delays dashboard go-live.",
        schedule_impact_days=7, recovery_action="Escalate to CFO for fast-track approval.",
        recovery_owner_id=users[4].id, revised_due_date=today + timedelta(days=5),
        management_intervention=True, preventive_action="Pre-approve vendor onboarding for critical projects.",
        approval_status="pending",
    ))

    # Backlog
    db.add_all([
        models.BacklogItem(code="BLG-0001", project_id=p1.id, requirement="Predictive maintenance model",
                           description="Train ML model on vibration data.", business_value="high", priority="high",
                           requested_by_id=users[4].id, status="grooming"),
        models.BacklogItem(code="BLG-0002", project_id=p1.id, requirement="Mobile alerts for downtime",
                           description="Push notifications to supervisors.", business_value="medium", priority="medium",
                           requested_by_id=users[4].id, status="new"),
    ])

    # Meeting + Decision + Management Action
    meeting = models.Meeting(title="Project Steering Committee — Feb", meeting_type="steering_committee", meeting_date=today - timedelta(days=7))
    db.add(meeting)
    db.flush()

    decision = models.Decision(code="DEC-0001", meeting_id=meeting.id, statement="Fast-track cloud procurement for plant IoT.",
                               owner_id=users[2].id, project_id=p1.id, decision_date=today - timedelta(days=7), status="open")
    db.add(decision)
    db.flush()

    db.add(models.ManagementAction(
        code="ACT-0001", meeting_id=meeting.id, decision_id=decision.id,
        action="CFO to approve cloud vendor onboarding within 48 hours.",
        responsible_id=users[2].id, accountable_id=users[0].id, due_date=today + timedelta(days=2), status="open",
    ))

    # Risk + Issue
    db.add(models.Risk(project_id=p1.id, description="Sensor vendor supply shortfall.", category="supply_chain",
                       likelihood="medium", impact="high", mitigation="Dual-source sensors.", owner_id=users[4].id, status="open"))
    db.add(models.Issue(project_id=p1.id, description="Cloud credentials delayed.", category="vendor",
                        severity="high", resolution="Escalated to CFO.", owner_id=users[4].id, status="open"))

    db.commit()


def _ensure_admin(db: Session):
    """Idempotently ensure the platform admin exists (for pre-existing databases)."""
    admin = db.query(models.User).filter(models.User.role == "admin").first()
    if admin:
        return
    company = db.query(models.Company).first()
    db.add(models.User(
        employee_id="E009", name="System Administrator", email="admin@anwargroup.com",
        designation="Platform Admin", role="admin",
        company_id=company.id if company else None,
    ))
    db.commit()


_LIST_OPTIONS = {
    "category": [
        "strategic", "project", "operational", "management_action", "compliance",
        "audit", "digital_transformation", "process_improvement", "technology",
        "finance", "procurement", "hr", "sales", "marketing", "supply_chain",
        "manufacturing", "maintenance", "commercial", "legal", "administration",
        "risk", "sustainability", "other",
    ],
    "task_type": [
        "task", "subtask", "action", "issue", "change", "bug", "approval",
        "review", "decision_followup", "compliance_action",
    ],
    "priority": ["low", "medium", "high", "critical"],
    "status": [
        "draft", "backlog", "ready", "in_progress", "in_review", "completed",
        "closed", "blocked", "on_hold", "cancelled",
    ],
}


def _seed_list_options(db: Session):
    for kind, values in _LIST_OPTIONS.items():
        for v in values:
            db.add(models.ListOption(kind=kind, value=v))
    db.commit()


def _ensure_list_options(db: Session):
    """Backfill list options for existing databases."""
    existing_kinds = {k for (k,) in db.query(models.ListOption.kind).distinct().all()}
    for kind, values in _LIST_OPTIONS.items():
        if kind in existing_kinds:
            continue
        for v in values:
            db.add(models.ListOption(kind=kind, value=v))
    db.commit()
