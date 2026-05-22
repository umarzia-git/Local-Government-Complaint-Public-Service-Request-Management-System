# Milestone 2 — ERD Design \& Normalization Report

**Project:** Local Government Complaint \& Public Service Request Management System (`lgc\\\_system`)  
**Database Engine:** InnoDB (MySQL 8.0)  
**Version:** 2.0  
**Status:** Fully Normalized to 3NF \& Verified via Milestone 4/5 Code Execution

\---

## Executive Summary

This document provides a formal breakdown of the normalization process applied to the `lgc\\\_system` database schema. Every structural asset defined in our DDL script has been scrutinized against First Normal Form (1NF), Second Normal Form (2NF), and Third Normal Form (3NF) to minimize redundancy, eliminate data anomalies (insertion, update, and deletion), and ensure strict relational data integrity.

\---

## Detailed Table-by-Table Normalization Analysis

### 1\. Table: `department`

* **Attributes:** `dept\\\_id` (PK), `dept\\\_name`, `head\\\_name`, `contact\\\_email`, `contact\\\_phone`

#### Normal Form Verification:

* **1NF (Satisfied):** All columns hold atomic values. There are no repeating groups or multi-valued attributes (e.g., multiple phone numbers are not concatenated into a single string; `contact\\\_phone` stores a single atomic value).
* **2NF (Satisfied):** The primary key is single-column (`dept\\\_id`). Since there is no composite primary key, partial dependencies are structurally impossible. Every non-key attribute is fully functionally dependent on `dept\\\_id`.
* **3NF (Satisfied):** No transitive dependencies exist. `dept\\\_name`, `head\\\_name`, `contact\\\_email`, and `contact\\\_phone` are properties of the department itself. None of these non-key columns depend on any other non-key column.

\---

### 2\. Table: `category`

* **Attributes:** `category\\\_id` (PK), `category\\\_name`, `dept\\\_id` (FK), `sla\\\_hours`, `description`

#### Normal Form Verification:

* **1NF (Satisfied):** All attributes contain scalar, individual values. The text block `description` stores a single summary, satisfying atomicity.
* **2NF (Satisfied):** The primary key is a single atomic identifier (`category\\\_id`). All non-prime attributes (`category\\\_name`, `sla\\\_hours`, `description`) depend on the entire primary key, eliminating partial dependency.
* **3NF (Satisfied):** The attribute `dept\\\_id` serves purely as a foreign key pointing to the managing department. The service resolution metric `sla\\\_hours` belongs directly to the specific problem type (`category\\\_id`) rather than the department at large. Thus, there are no transitive dependencies among non-prime attributes.

\---

### 3\. Table: `citizen`

* **Attributes:** `citizen\\\_id` (PK), `cnic`, `full\\\_name`, `email`, `phone`, `ward\\\_no`, `address`, `password\\\_hash`, `registered\\\_at`

#### Normal Form Verification:

* **1NF (Satisfied):** Every record contains individual scalar values. Pakistani CNICs are stored uniformly as a unique `VARCHAR(15)` string. Addresses are stored as atomic text segments.
* **2NF (Satisfied):** Supported by a single primary key (`citizen\\\_id`). Non-prime attributes such as `full\\\_name` and `password\\\_hash` depend thoroughly on the specific user identity, satisfying 2NF.
* **3NF (Satisfied):** While `ward\\\_no` reflects an operational geopolitical location, the user's specific residential `address` does not functionally determine the structural ward boundaries or vice versa in a standard user table profile. Because there is no functional dependency between `phone`/`email` and `ward\\\_no`, transitive dependency is avoided, fulfilling 3NF rules.

\---

### 4\. Table: `staff`

* **Attributes:** `staff\\\_id` (PK), `dept\\\_id` (FK), `full\\\_name`, `email`, `password\\\_hash`, `role`, `is\\\_active`, `created\\\_at`

#### Normal Form Verification:

* **1NF (Satisfied):** The `role` attribute utilizes an atomic native `ENUM('staff','admin')`, and security hashes are stored as single continuous strings (`VARCHAR(255)`).
* **2NF (Satisfied):** Single primary key entity structure. No composite parameters are present; all employee traits are dependent on `staff\\\_id`.
* **3NF (Satisfied):** An employee's structural department association is explicitly handled by the foreign key reference column `dept\\\_id`. The user properties (`email`, `password\\\_hash`, administrative `role`) belong natively to the individual employee account and do not reveal hidden operational data dependencies elsewhere.

\---

### 5\. Table: `complaint`

* **Attributes:** `complaint\\\_id` (PK), `token`, `citizen\\\_id` (FK), `category\\\_id` (FK), `dept\\\_id` (FK), `ward\\\_no`, `description`, `photo\\\_path`, `status`, `priority`, `sla\\\_deadline`, `feedback\\\_pending`, `filed\\\_at`, `resolved\\\_at`

#### Normal Form Verification:

* **1NF (Satisfied):** File paths (`photo\\\_path`) and audit dates (`filed\\\_at`, `resolved\\\_at`) are stored as single atomic strings and datetime primitives.
* **2NF (Satisfied):** Fully conforms to 2NF. All transactional metrics depend entirely on the unique auto-increment primary token identifier `complaint\\\_id`.
* **3NF (Satisfied - Crucial Justification):** This table contains `category\\\_id` and `dept\\\_id` simultaneously. In basic database structures, this might risk a Transitive Dependency violation because a `category` belongs to a specific `department` (i.e., Complaint -> Category -> Department).

*Why this design does NOT violate 3NF:* Including `dept\\\_id` directly inside the `complaint` table is an explicit application safety measure designed to handle cases where a complaint might be reassigned to a different department without changing the original underlying issue category. Because `dept\\\_id` can vary independently from the default department mapped inside the `category` master table during live operations, it is a direct functional attribute of the individual transaction (`complaint\\\_id`), satisfying 3NF.

\---

### 6\. Table: `status\\\_log`

* **Attributes:** `log\\\_id` (PK), `complaint\\\_id` (FK), `staff\\\_id` (FK), `old\\\_status`, `new\\\_status`, `note`, `changed\\\_at`

#### Normal Form Verification:

* **1NF (Satisfied):** Historical tracking fields, state transition values (`ENUM`), and timestamps are strictly scalar.
* **2NF (Satisfied):** The audit history entry relies entirely on the unique surrogate token `log\\\_id`.
* **3NF (Satisfied):** This table represents a historical ledger. The log entries are strictly dependent on `log\\\_id`. It stores snapshots of the changing state of a complaint managed by an individual system agent. No transitive relationships exist between `old\\\_status`, `new\\\_status`, and the `staff\\\_id`.

\---

### 7\. Table: `complaint\\\_feedback`

* **Attributes:** `feedback\\\_id` (PK), `complaint\\\_id` (FK), `citizen\\\_id` (FK), `dept\\\_id` (FK), `rating`, `comments`, `submitted\\\_at`

#### Normal Form Verification:

* **1NF (Satisfied):** Clean atomic values. Satisfies `CHK\\\_RATING` constraints natively limiting range integer options strictly between 1 and 5.
* **2NF (Satisfied):** Single primary key (`feedback\\\_id`) prevents any partial dependencies.
* **3NF (Satisfied):** While `complaint\\\_id`, `citizen\\\_id`, and `dept\\\_id` are co-located, they represent distinct transactional reference dimensions of a customer satisfaction record. The user `rating` and personal `comments` depend directly on the unique `feedback\\\_id` instance. No non-key attributes determine each other.

\---

### 8\. Table: `chronic\\\_issue`

* **Attributes:** `chronic\\\_id` (PK), `category\\\_id` (FK), `ward\\\_no`, `complaint\\\_count`, `detected\\\_at`, `is\\\_resolved`, `resolution\\\_note`

#### Normal Form Verification:

* **1NF (Satisfied):** Simple numeric indicators, flag arrays (`TINYINT`), and strings mapped atomically.
* **2NF (Satisfied):** Relies on a single independent primary identifier (`chronic\\\_id`).
* **3NF (Satisfied):** This table is populated dynamically via our database engine's backend pipeline (`trg\\\_detect\\\_recurring`). It acts as a tracking ledger for recurring neighborhood anomalies. The aggregate value `complaint\\\_count` is an isolated evaluation of a specific issue type (`category\\\_id`) within a physical zone (`ward\\\_no`) at a targeted point in time (`detected\\\_at`). There are no non-prime structural dependencies.

\---

## Step 2 — Redundancy \& Duplicate Removal Action Log

During our systematic schema refinement, several redundant data layers were analyzed and removed to protect against structural data anomalies:

|Table Inspected|Potential Redundancy Identified|Action Taken \& Structural Justification|
|-|-|-|
|`category`|Department Head Name / Contact Info|**Removed/Excluded.** These traits are kept strictly inside the parent `department` table. Referencing `dept\\\_id` as a foreign key allows us to pull this data dynamically using SQL `JOIN` statements, preventing update anomalies.|
|`complaint`|Citizen Name and Phone Number|**Removed/Excluded.** Storing citizen contact details inside individual complaint rows would violate 2NF/3NF. This information is looked up at runtime by linking the `citizen\\\_id` foreign key back to the master `citizen` table.|
|`status\\\_log`|Department ID|**Removed/Excluded.** The department context is retrieved dynamically via the `complaint\\\_id` or the assigned agent's `staff\\\_id`. Removing it prevents data synchronization errors across workflow updates.|
|`chronic\\\_issue`|Raw Complaint List Array|**Normalized via Trigger.** Instead of saving duplicate rows or complex text patterns inside the complaint records, a clean trigger `trg\\\_detect\\\_recurring` runs a background aggregation query (`COUNT(\\\*)`) and records the anomaly cleanly in this specialized tracking table.|

\---

## Step 3 — ERD Relationship \& Cardinality Map

All normalization changes have been verified and matched against our Enhanced Entity-Relationship (EER) model. The schema enforces the following structural relationships:

* **`department` -> `category`** -> `1:M` (One department manages multiple service types. Protected via `ON DELETE RESTRICT` to prevent orphaned categories).
* **`department` -> `staff`** -> `1:M` (One department employs multiple system operators).
* **`citizen` -> `complaint`** -> `1:M` (One citizen can submit multiple complaints over time).
* **`category` -> `complaint`** -> `1:M` (One problem category can be assigned to multiple independent complaints).
* **`complaint` -> `status\\\_log`** -> `1:M` (One complaint creates a running historical trail of status updates. Enforces `ON DELETE CASCADE`).
* **`complaint` -> `complaint\\\_feedback`** -> `1:1` (Enforced via a unique constraint `uq\\\_feedback\\\_compl`. A complaint can only receive one citizen satisfaction survey response).
* **`category` -> `chronic\\\_issue`** -> `1:M` (A recurring issue alert points directly to a specific master category record).

