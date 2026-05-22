-- ============================================================
--  Milestone 5 — DML Script (Data Population + Validation)
--  Project : Local Government Complaint & Public Service
--            Request Management System
--  Version : 1.0  |  Date : 17 May 2026
--  Commit  : M5: Data populated validation queries added
-- ============================================================

USE lgc_system;

-- NOTE: All core datasets (50-100 rows) have been successfully 
-- populated using the MySQL Workbench Table Data Import Wizard.

-- ============================================================
-- REQUIRED DATA OPERATIONS (YOUR UPDATES & DELETES)
-- ============================================================

-- 1) UPDATE: In Progress complaint ko Resolve karna
UPDATE complaint
SET status = 'Resolved',
    resolved_at = NOW()
WHERE complaint_id = 2
  AND status = 'In Progress';

-- 2) UPDATE: Complaint ki routing theek karna
UPDATE complaint
SET dept_id = 2,
    category_id = 3
WHERE complaint_id = 4;

-- 3) DELETE: Received status wali complaint ko remove karna
DELETE FROM complaint
WHERE token = 'LGC-2026-00010'
  AND status = 'Received';


-- ============================================================
-- MANDATORY VALIDATION QUERIES (As required by Milestone 5)
-- ============================================================

-- VALIDATION A: COUNT (*) for each table to confirm row counts
SELECT 'department' AS table_name, COUNT(*) AS row_count FROM department
UNION ALL
SELECT 'category', COUNT(*) FROM category
UNION ALL
SELECT 'citizen', COUNT(*) FROM citizen
UNION ALL
SELECT 'staff', COUNT(*) FROM staff
UNION ALL
SELECT 'complaint', COUNT(*) FROM complaint
UNION ALL
SELECT 'status_log', COUNT(*) FROM status_log
UNION ALL
SELECT 'complaint_feedback', COUNT(*) FROM complaint_feedback
UNION ALL
SELECT 'chronic_issue', COUNT(*) FROM chronic_issue;

-- VALIDATION B: A NULL check on key columns (Primary Keys)
SELECT 
    SUM(CASE WHEN dept_id IS NULL THEN 1 ELSE 0 END) AS null_dept,
    SUM(CASE WHEN citizen_id IS NULL THEN 1 ELSE 0 END) AS null_citizen,
    SUM(CASE WHEN complaint_id IS NULL THEN 1 ELSE 0 END) AS null_complaint
FROM complaint;

-- VALIDATION C: A JOIN-based check to confirm foreign key integrity
SELECT 
    COUNT(c.complaint_id) AS total_inspected,
    SUM(CASE WHEN cit.citizen_id IS NULL THEN 1 ELSE 0 END) AS unmapped_citizens,
    SUM(CASE WHEN cat.category_id IS NULL THEN 1 ELSE 0 END) AS unmapped_categories,
    SUM(CASE WHEN d.dept_id IS NULL THEN 1 ELSE 0 END) AS unmapped_departments
FROM complaint c
LEFT JOIN citizen cit ON c.citizen_id = cit.citizen_id
LEFT JOIN category cat ON c.category_id = cat.category_id
LEFT JOIN department d ON c.dept_id = d.dept_id;

-- ============================================================
-- END OF SCRIPT
-- ============================================================