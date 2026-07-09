# LGC System — Local Government Complaint Management System

A full-stack web application that lets citizens file and track complaints about civic issues (water supply, road damage, electricity, sanitation), while staff resolve them and admins monitor department performance through automated analytics and dashboards.

Built as a database-driven Flask application backed by MySQL, with SQL views and triggers doing the heavy lifting for KPI reporting and recurring-issue detection.

---

## Features

- **Role-based access** — separate login flows and dashboards for Citizens, Staff, and Admins
- **Complaint management** — citizens file complaints against a category/department, track status, and submit feedback after resolution
- **Public complaint tracking** — anyone can track a complaint's status using its token, no login required
- **SLA tracking** — every complaint gets an SLA deadline based on its category; breaches are tracked automatically
- **Admin dashboards** — department KPIs, ward-level risk heatmap, chronic/recurring issue detection, and citizen satisfaction ratings
- **Chart.js visualizations** — visual breakdown of complaint status, department performance, and ward risk on the admin dashboard
- **Staff management** — admins can add, deactivate, and reactivate staff accounts
- **Automated SQL triggers** — auto-detects recurring complaints in the same ward/category and flags them as chronic issues; auto-prompts citizens for feedback once a complaint is resolved

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask (Python) |
| Database | MySQL |
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js |
| Auth | Werkzeug password hashing |
| Deployment | Gunicorn + Railway |

---

## Demo Credentials

Seed the demo accounts locally with `python seed_demo.py`, then log in with:

| Role | Email | Password |
|---|---|---|
| Citizen | `citizen@demo.com` | `demo123` |
| Staff | `staff@demo.com` | `demo123` |
| Admin | `admin@demo.com` | `admin123` |

---

## How to Run Locally

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd lgc-system
```

**2. Create a virtual environment and install dependencies**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

**3. Set up the database**
```sql
source schema.sql
```

**4. Configure environment variables**

Copy `.env.example` to `.env` and fill in your local MySQL credentials:
```bash
cp .env.example .env
```

**5. Seed demo accounts**
```bash
python seed_demo.py
```

**6. Run the app**
```bash
python app.py
```

The app will be available at `http://localhost:5000`.

---

## Screenshots

> _Add screenshots here once available._

| Page | Preview |
|---|---|
| Citizen Dashboard | _placeholder_ |
| Staff Dashboard | _placeholder_ |
| Admin Dashboard | _placeholder_ |
| Complaint Tracking | _placeholder_ |
