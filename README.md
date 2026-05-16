# Local Government Complaint & Public Service Request Management System
## Database Systems Lab — Semester Project

**Group Members:** Omer Zia | Yahya Usman  
**Program & Group:** BSCS — Group A  
**Institution:** IMSciences  

---

## Project Overview

A web-based complaint management system for local government (tehsil/municipal level). Citizens file complaints about civic issues (water, roads, electricity, sanitation), staff resolves them, and admins monitor performance through automated analytics.

---

## Repository Structure

```
DBLab_Project/
│
├── ERD/
│   ├── erd_v1.png              ← Initial ERD (Milestone 1)
│   └── erd_updated.png         ← Updated ERD after normalization (Milestone 2)
│
├── Normalization/
│   └── NORMALIZATION.md        ← 1NF → 2NF → 3NF with justifications
│
├── Dataflow/
│   └── dataflow.md             ← How data enters, moves, and exits the system
│
├── CSV/
│   ├── department.csv          ← 4 rows
│   ├── category.csv            ← 8 rows
│   ├── citizen.csv             ← 80 rows
│   ├── staff.csv               ← 20 rows
│   ├── complaint.csv           ← 100 rows
│   ├── status_log.csv          ← 150 rows
│   ├── complaint_feedback.csv  ← ~50 rows
│   └── chronic_issue.csv       ← 20 rows
│
├── SQL/
│   ├── ddl.sql                 ← CREATE TABLE + indexes + triggers + views
│   ├── dml.sql                 ← INSERT + UPDATE + DELETE statements
│   └── validation_queries.sql  ← COUNT, NULL check, FK integrity, JOINs
│
├── Docs/
│   └── Final_PDF.pdf           ← Compiled submission PDF
│
└── README.md
```

---

## Database Schema (8 Tables)

| Table | Rows | Description |
|-------|------|-------------|
| department | 4 | Government departments |
| category | 8 | Complaint types mapped to departments |
| citizen | 80 | Registered citizens |
| staff | 20 | Department employees |
| complaint | 100 | Core complaint records |
| status_log | 150 | Audit trail of every status change |
| complaint_feedback | ~50 | Citizen ratings after resolution |
| chronic_issue | 20 | Auto-detected recurring problem areas |

---

## Innovation Features

### Innovation 1 - Ward Risk Heatmap
SQL stored procedure computes a weighted risk score per ward daily. Exposed via `v_ward_heatmap` VIEW.

### Innovation 2 - Auto-Escalation Trigger
`trg_detect_recurring` fires on every complaint INSERT. If 3+ same-category complaints appear in the same ward within 7 days, the system auto-creates a chronic_issue record and marks the complaint CRITICAL.

### Innovation 3 - Citizen KPI Feedback Loop
`trg_feedback_on_resolve` fires when complaint status changes to Resolved. Sets `feedback_pending = 1`. Citizen submits rating → stored in complaint_feedback → aggregated in `v_department_kpi` VIEW.

---

## Commit History

| Commit | Message |
|--------|---------|
| M1 | Initial ERD and schema designed |
| M2 | Applied 1NF–3NF normalization, updated ERD and schema |
| M3 | Synthetic data generated; dataflow documented |
| M4 | DDL scripts added, EER diagram verified |
| M5 | Data populated, validation queries added |

---

## Technology Stack

- **Database:** MySQL 8.0
- **ERD Tool:** MySQL Workbench
- **Data Generation:** Python (Faker library)
- **Version Control:** Git + GitHub
