# Enterprise Task & Project Management System

[![Frontend Status](https://img.shields.io/badge/Frontend-Vercel-black?style=flat-square&logo=vercel)](https://task-project-management-ten.vercel.app)
[![Backend Status](https://img.shields.io/badge/Backend-Render-informational?style=flat-square&logo=render)](https://task-project-management-pqw2.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](https://react.dev/)

An enterprise-grade full-stack task and project management solution built to streamline organizational workflows, governance, task life-cycle tracking, RACI matrix assignments, and automated email notification schedules.

---

## 🌐 Live System Links

* **Live Application (Frontend):** [https://task-project-management-ten.vercel.app](https://task-project-management-ten.vercel.app)
* **API Documentation (Swagger UI):** [https://task-project-management-pqw2.onrender.com/docs](https://task-project-management-pqw2.onrender.com/docs)
* **Backend Base API URL:** [https://task-project-management-pqw2.onrender.com](https://task-project-management-pqw2.onrender.com)

---

## 🚀 Key Features

* **Authentication & Authorization:** Secure JWT token-based authentication with password hashing, reset mechanisms, and user management.
* **Project & Task Lifecycle:** Multi-organization support, task assignments, backlog tracking, delay logs, and multi-tier approvals.
* **Governance & RACI Matrix:** Governance tracking and RACI (Responsible, Accountable, Consulted, Informed) matrix mapping across tasks and departments.
* **Automated Email Scheduler:** Integrated background scheduler (APScheduler) for dispatching automated email notifications and daily task summary reports.
* **Executive Dashboards & Audit Trails:** Real-time visibility into project metrics, backlog health, and system-wide audit logging.

---

## 🛠 Tech Stack

### **Frontend**
* **Framework:** React 18 with TypeScript
* **Build Tool:** Vite 6
* **Routing:** React Router DOM (v6)
* **Deployment:** Vercel

### **Backend**
* **Framework:** FastAPI (Python 3.11)
* **Database ORM:** SQLAlchemy
* **Database:** PostgreSQL (Neon Serverless Cloud)
* **Security & Auth:** Passlib with `bcrypt==4.0.1`, PyJWT
* **Background Jobs:** APScheduler (Email notifications & background sync)
* **Deployment:** Render

---

## 📂 Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── routers/             # API Endpoints (auth, tasks, projects, governance, etc.)
│   │   ├── models.py            # SQLAlchemy database schemas
│   │   ├── database.py          # Database connection configuration
│   │   ├── auth.py              # Auth routes & login endpoints
│   │   ├── security.py          # Password hashing and token generation
│   │   ├── scheduler.py         # Automated email cron job scheduler
│   │   ├── config.py            # Environment settings parser
│   │   └── main.py              # Application entry point & CORS configuration
│   └── requirements.txt         # Python dependencies
│
└── frontend/
    ├── src/                     # React components, pages, and API services
    ├── package.json             # NPM scripts and dependencies
    └── vite.config.ts           # Vite configuration
