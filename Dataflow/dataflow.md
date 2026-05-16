# Dataflow Description — Milestone 3
## Local Government Complaint & Public Service Request Management System

**Group Members:** [Student 1 Name] | [Student 2 Name]  
**Date:** 17 May 2026

---

## Overview

This document describes exactly how data enters, moves through, and exits the Local Government Complaint & Public Service Request Management System. Every data path is specific to our schema and our three innovation features.

---

## 1. Data Entry Points

Data enters the system through three distinct interfaces:

### 1.1 Citizen Registration & Complaint Submission
- A citizen fills the registration form → data INSERT into **CITIZEN** table (`citizen_id`, `cnic`, `full_name`, `email`, `phone`, `ward_no`, `password_hash`, `registered_at`)
- After login, citizen fills complaint form → data INSERT into **COMPLAINT** table
- At INSERT time, `sla_deadline` is auto-calculated as `filed_at + sla_hours` (fetched from CATEGORY via `category_id`)
- A unique `token` is generated (format: `LGC-YYYY-NNNNN`) and stored
- **Trigger fires immediately:** `trg_detect_recurring` checks COMPLAINT table for 3+ same category+ward in 7 days → if true, INSERT into **CHRONIC_ISSUE** and UPDATE priority to CRITICAL

### 1.2 Staff Status Updates
- Staff logs in, selects assigned complaint, updates status
- UPDATE on **COMPLAINT** table (`status`, optionally `resolved_at`)
- Simultaneously, INSERT into **STATUS_LOG** (`complaint_id`, `staff_id`, `old_status`, `new_status`, `note`, `changed_at`) — this is the audit trail
- **Trigger fires:** `trg_feedback_on_resolve` — if new status = 'Resolved', sets `feedback_pending = 1` in COMPLAINT

### 1.3 Citizen Feedback Submission
- After complaint resolved, citizen sees rating prompt (feedback_pending = 1)
- Citizen submits 1–5 star rating → INSERT into **COMPLAINT_FEEDBACK** (`complaint_id`, `citizen_id`, `dept_id`, `rating`, `comments`, `submitted_at`)

### 1.4 Admin Data Entry
- Admin can INSERT/UPDATE department details → **DEPARTMENT** table
- Admin can INSERT/UPDATE complaint categories → **CATEGORY** table
- Admin can INSERT new staff accounts → **STAFF** table
- Admin can manually UPDATE complaint priority, status, dept_id (reassign)

---

## 2. Data Flow Through Tables (Dependency Order)

The tables have a strict dependency order — some tables must be populated before others:

```
DEPARTMENT
    ↓
CATEGORY ──────────────────────────────────────────────┐
    ↓                                                   │
CITIZEN          STAFF                                  │
    ↓               ↓                                   ↓
    └──────────→ COMPLAINT ←───────────────────── CHRONIC_ISSUE
                    ↓         (trigger auto-creates)
              STATUS_LOG
              COMPLAINT_FEEDBACK
```

**Load Order for Milestone 5:**
1. DEPARTMENT (no dependencies)
2. CATEGORY (depends on DEPARTMENT)
3. CITIZEN (no dependencies)
4. STAFF (depends on DEPARTMENT)
5. COMPLAINT (depends on CITIZEN, CATEGORY, DEPARTMENT)
6. STATUS_LOG (depends on COMPLAINT, STAFF)
7. COMPLAINT_FEEDBACK (depends on COMPLAINT, CITIZEN, DEPARTMENT)
8. CHRONIC_ISSUE (depends on CATEGORY)

---

## 3. Data Processing (Inside the Database)

### 3.1 Automatic Processing via Triggers
| Trigger | Event | What Happens |
|---------|-------|-------------|
| `trg_detect_recurring` | AFTER INSERT on COMPLAINT | Counts same category+ward complaints in 7 days. If ≥3: INSERT chronic_issue, UPDATE complaint priority = CRITICAL |
| `trg_feedback_on_resolve` | AFTER UPDATE on COMPLAINT | If status changes to 'Resolved': SET feedback_pending = 1, SET resolved_at = NOW() |

### 3.2 Computed Data via Views
| View | Input Tables | Output |
|------|-------------|--------|
| `v_department_kpi` | COMPLAINT + COMPLAINT_FEEDBACK + DEPARTMENT | avg_rating, total_resolved, on_time_pct per department |
| `v_ward_heatmap` | COMPLAINT + COMPLAINT_FEEDBACK | risk_score per ward (weighted: 40% open complaints + 35% SLA breaches + 25% inverse satisfaction) |

### 3.3 Nightly Processing via Stored Procedure
- `sp_calc_ward_risk` runs nightly — aggregates ward data and writes to `ward_risk_scores` table for admin dashboard

---

## 4. Data Output

| Output | Source | Consumer |
|--------|--------|----------|
| Complaint status (by token) | SELECT from COMPLAINT WHERE token = ? | Citizen tracking portal |
| Assigned complaints list | SELECT from COMPLAINT WHERE dept_id = ? AND status != 'Resolved' | Staff dashboard |
| All complaints + filters | SELECT with JOINs on COMPLAINT, CITIZEN, CATEGORY | Admin panel |
| Ward heatmap data | SELECT from v_ward_heatmap | Admin dashboard map |
| Department KPI scores | SELECT from v_department_kpi | Admin reports page |
| SLA breach alerts | SELECT from COMPLAINT WHERE sla_deadline < NOW() AND status NOT IN ('Resolved','Closed') | Admin alert panel |
| Chronic issues list | SELECT from CHRONIC_ISSUE WHERE is_resolved = 0 | Admin dashboard |
| Audit history per complaint | SELECT from STATUS_LOG WHERE complaint_id = ? ORDER BY changed_at | Admin complaint detail view |

---

## 5. Data Lifecycle Summary

```
Citizen Registers
       ↓
   [CITIZEN table]
       ↓
Citizen Files Complaint
       ↓
   [COMPLAINT table] ←── sla_deadline auto-set
       ↓
   [trg_detect_recurring fires]
       ↓ (if 3+ same complaints)
   [CHRONIC_ISSUE created]
       ↓
Staff Updates Status
       ↓
   [STATUS_LOG entry created]  ←── every change recorded
       ↓ (if Resolved)
   [trg_feedback_on_resolve fires]
       ↓
   [feedback_pending = 1 in COMPLAINT]
       ↓
Citizen Submits Rating
       ↓
   [COMPLAINT_FEEDBACK created]
       ↓
   [v_department_kpi updates automatically]
       ↓
Admin Views Reports & Heatmap
       ↓
   [v_ward_heatmap — risk scores]
   [v_department_kpi — performance]
```

---

## Commit Message for This Milestone
```
M3: Synthetic data generated (50–100 rows per table); dataflow documented
```
