# Milestone 2 — ERD Design & Normalization Report

**Project:** Local Government Complaint & Public Service Request Management System (`lgc_system`)  
**Database Engine:** InnoDB (MySQL 8.0)  
**Version:** 2.0  
**Status:** Fully Normalized to 3NF & Verified via Milestone 4/5 Code Execution

---

## Executive Summary
This document provides a formal breakdown of the normalization process applied to the `lgc_system` database schema. Every structural asset defined in our DDL script has been scrutinized against First Normal Form (1NF), Second Normal Form (2NF), and Third Normal Form (3NF) to minimize redundancy, eliminate data anomalies (insertion, update, and deletion), and ensure strict relational data integrity.

---

## Detailed Table-by-Table Normalization Analysis

### 1. Table: `department`
* **Attributes:** `dept_id` (PK), `dept_name`, `head_name`, `contact_email`, `contact_phone`

#### Normal Form Verification:
* **1NF (Satisfied):** All columns hold atomic values. There are no repeating groups or multi-valued attributes (e.g., multiple phone numbers are not concatenated into a single string; `contact_phone` stores a single atomic value).
* **2NF (Satisfied):** The primary key is single-column (`dept_id`). Since there is no composite primary key, partial dependencies are structurally impossible. Every non-key attribute is fully functionally dependent on `dept_id`.
* **3NF (Satisfied):** No transitive dependencies exist. `dept_name`, `head_name`, `contact_email`, and `contact_phone` are properties of the department itself. None of these non-key columns depend on any other non-key column.

---

### 2. Table: `category`
* **Attributes:** `category_id` (PK), `category_name`, `dept_id` (FK), `sla_hours`, `description`

#### Normal Form Verification:
* **1NF (Satisfied):** All attributes contain scalar, individual values. The text block `description` stores a single summary, satisfying atomicity.
* **2NF (Satisfied):** The primary key is a single atomic identifier (`category_id`). All non-prime attributes (`category_name`, `sla_hours`, `description`) depend on the entire primary key, eliminating partial dependency.
* **3NF (Satisfied):** The attribute `dept_id` serves purely as a foreign key pointing to the managing department. The service resolution metric `sla_hours` belongs directly to the specific problem type (`category_id`) rather than the department at large. Thus, there are no transitive dependencies among non-prime attributes.

---

### 3. Table: `citizen`
* **Attributes:** `citizen_id` (PK), `cnic`, `full_name`, `email`, `phone`, `ward_no`, `address`, `password_hash`, `registered_at`

#### Normal Form Verification:
* **1NF (Satisfied):** Every record contains individual scalar values. Pakistani CNICs are stored uniformly as a unique `VARCHAR(15)` string. Addresses are stored as atomic text segments.
* **2NF (Satisfied):** Supported by a single primary key (`citizen_id`). Non-prime attributes such as `full_name` and `password_hash` depend thoroughly on the specific user identity, satisfying 2NF.
* **3NF (Satisfied):** While `ward_no` reflects an operational geopolitical location, the user's specific residential `address` does not functionally determine the structural ward boundaries or vice versa in a standard user table profile. Because there is no functional dependency between `phone`/`email` and `ward_no`, transitive dependency is avoided, fulfilling 3NF rules.

---

### 4. Table: `staff`
* **Attributes:** `staff_id` (PK), `dept_id` (FK), `full_name`, `email`, `password_hash`, `role`, `is_active`, `created_at`

#### Normal Form Verification:
* **1NF (Satisfied):** The `role` attribute utilizes an atomic native `ENUM('staff','admin')`, and security hashes are stored as single continuous strings (`VARCHAR(255)`).
* **2NF (Satisfied):** Single primary key entity structure. No composite parameters are present; all employee traits are dependent on `staff_id`.
* **3NF (Satisfied):** An employee's structural department association is explicitly handled by the foreign key reference column `dept_id`. The user properties (`email`, `password_hash`, administrative `role`) belong natively to the individual employee account and do not reveal hidden operational data dependencies elsewhere.

---

### 5. Table: `complaint`
* **Attributes:** `complaint_id` (PK), `token`, `citizen_id` (FK), `category_id` (FK), `dept_id` (FK), `ward_no`, `description`, `photo_path`, `status`, `priority`, `sla_deadline`, `feedback_pending`, `filed_at`, `resolved_at`

#### Normal Form Verification:
* **1NF (Satisfied):** File paths (`photo_path`) and audit dates (`filed_at`, `resolved_at`) are stored as single atomic strings and datetime primitives.
* **2NF (Satisfied):** Fully conforms to 2NF. All transactional metrics depend entirely on the unique auto-increment primary token identifier `complaint_id`.
* **3NF (Satisfied - Crucial Justification):** This table contains `category_id` and `dept_id` simultaneously. In basic database structures, this might risk a Transitive Dependency violation because a `category` belongs to a specific `department` (i.e., Complaint -> Category -> Department). 

*Why this design does NOT violate 3NF:* Including `dept_id` directly inside the `complaint` table is an explicit application safety measure designed to handle cases where a complaint might be reassigned to a different department without changing the original underlying issue category. Because `dept_id` can vary independently from the default department mapped inside the `category` master table during live operations, it is a direct functional attribute of the individual transaction (`complaint_id`), satisfying 3NF.

---

### 6. Table: `status_log`
* **Attributes:** `log_id` (PK), `complaint_id` (FK), `staff_id` (FK), `old_status`, `new_status`, `note`, `changed_at`

#### Normal Form Verification:
* **1NF (Satisfied):** Historical tracking fields, state transition values (`ENUM`), and timestamps are strictly scalar.
* **2NF (Satisfied):** The audit history entry relies entirely on the unique surrogate token `log_id`.
* **3NF (Satisfied):** This table represents a historical ledger. The log entries are strictly dependent on `log_id`. It stores snapshots of the changing state of a complaint managed by an individual system agent. No transitive relationships exist between `old_status`, `new_status`, and the `staff_id`.

---

### 7. Table: `complaint_feedback`
* **Attributes:** `feedback_id` (PK), `complaint_id` (FK), `citizen_id` (FK), `dept_id` (FK), `rating`, `comments`, `submitted_at`

#### Normal Form Verification:
* **1NF (Satisfied):** Clean atomic values. Satisfies `CHK_RATING` constraints natively limiting range integer options strictly between 1 and 5.
* **2NF (Satisfied):** Single primary key (`feedback_id`) prevents any partial dependencies.
* **3NF (Satisfied):** While `complaint_id`, `citizen_id`, and `dept_id` are co-located, they represent distinct transactional reference dimensions of a customer satisfaction record. The user `rating` and personal `comments` depend directly on the unique `feedback_id` instance. No non-key attributes determine each other.

---

### 8. Table: `chronic_issue`
* **Attributes:** `chronic_id` (PK), `category_id` (FK), `ward_no`, `complaint_count`, `detected_at`, `is_resolved`, `resolution_note`

#### Normal Form Verification:
* **1NF (Satisfied):** Simple numeric indicators, flag arrays (`TINYINT`), and strings mapped atomically.
* **2NF (Satisfied):** Relies on a single independent primary identifier (`chronic_id`).
* **3NF (Satisfied):** This table is populated dynamically via our database engine's backend pipeline (`trg_detect_recurring`). It acts as a tracking ledger for recurring neighborhood anomalies. The aggregate value `complaint_count` is an isolated evaluation of a specific issue type (`category_id`) within a physical zone (`ward_no`) at a targeted point in time (`detected_at`). There are no non-prime structural dependencies.

---

## Step 2 — Redundancy & Duplicate Removal Action Log

During our systematic schema refinement, several redundant data layers were analyzed and removed to protect against structural data anomalies:

| Table Inspected | Potential Redundancy Identified | Action Taken & Structural Justification |
| :--- | :--- | :--- |
| `category` | Department Head Name / Contact Info | **Removed/Excluded.** These traits are kept strictly inside the parent `department` table. Referencing `dept_id` as a foreign key allows us to pull this data dynamically using SQL `JOIN` statements, preventing update anomalies. |
| `complaint` | Citizen Name and Phone Number | **Removed/Excluded.** Storing citizen contact details inside individual complaint rows would violate 2NF/3NF. This information is looked up at runtime by linking the `citizen_id` foreign key back to the master `citizen` table. |
| `status_log` | Department ID | **Removed/Excluded.** The department context is retrieved dynamically via the `complaint_id` or the assigned agent's `staff_id`. Removing it prevents data synchronization errors across workflow updates. |
| `chronic_issue` | Raw Complaint List Array | **Normalized via Trigger.** Instead of saving duplicate rows or complex text patterns inside the complaint records, a clean trigger `trg_detect_recurring` runs a background aggregation query (`COUNT(*)`) and records the anomaly cleanly in this specialized tracking table. |

---

## Step 3 — ERD Relationship & Cardinality Map

All normalization changes have been verified and matched against our Enhanced Entity-Relationship (EER) model. The schema enforces the following structural relationships:

* **`department` -> `category`** -> `1:M` (One department manages multiple service types. Protected via `ON DELETE RESTRICT` to prevent orphaned categories).
* **`department` -> `staff`** -> `1:M` (One department employs multiple system operators).
* **`citizen` -> `complaint`** -> `1:M` (One citizen can submit multiple complaints over time).
* **`category` -> `complaint`** -> `1:M` (One problem category can be assigned to multiple independent complaints).
* **`complaint` -> `status_log`** -> `1:M` (One complaint creates a running historical trail of status updates. Enforces `ON DELETE CASCADE`).
* **`complaint` -> `complaint_feedback`** -> `1:1` (Enforced via a unique constraint `uq_feedback_compl`. A complaint can only receive one citizen satisfaction survey response).
* **`category` -> `chronic_issue`** -> `1:M` (A recurring issue alert points directly to a specific master category record).