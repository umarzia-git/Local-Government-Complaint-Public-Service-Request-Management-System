-- ============================================================
--  Milestone 5 — Ultimate Custom Validation Suite (Separated)
--  Run this to generate clean, individual professional tables.
-- ============================================================

USE lgc_system;

-- ────────────────────────────────────────────────────────────
-- TAB 1: SYSTEM ROW COUNTS (Stuctural Verification)
-- ────────────────────────────────────────────────────────────
-- Target: Proves that all data from CSVs migrated fully into the schema.
SELECT '1. System Volume Check' AS inspection_type, 'department' AS table_name, COUNT(*) AS row_count FROM department
UNION ALL
SELECT '1. System Volume Check', 'category', COUNT(*) FROM category
UNION ALL
SELECT '1. System Volume Check', 'citizen', COUNT(*) FROM citizen
UNION ALL
SELECT '1. System Volume Check', 'staff', COUNT(*) FROM staff
UNION ALL
SELECT '1. System Volume Check', 'complaint', COUNT(*) FROM complaint
UNION ALL
SELECT '1. System Volume Check', 'status_log', COUNT(*) FROM status_log
UNION ALL
SELECT '1. System Volume Check', 'complaint_feedback', COUNT(*) FROM complaint_feedback
UNION ALL
SELECT '1. System Volume Check', 'chronic_issue', COUNT(*) FROM chronic_issue;


-- ────────────────────────────────────────────────────────────
-- TAB 2: DATA INTEGRITY — CRITICAL NULL DETECTION
-- ────────────────────────────────────────────────────────────
-- Target: All metrics MUST return 0. Any row here shows missing required data.
SELECT 'citizen table' AS checked_table, 'cnic, full_name, email, phone' AS columns_verified, COUNT(*) AS null_errors FROM citizen WHERE cnic IS NULL OR full_name IS NULL OR email IS NULL OR phone IS NULL
UNION ALL
SELECT 'complaint table', 'token, citizen, category, dept, status', COUNT(*) FROM complaint WHERE token IS NULL OR citizen_id IS NULL OR category_id IS NULL OR dept_id IS NULL OR description IS NULL OR status IS NULL
UNION ALL
SELECT 'staff table', 'full_name, email, role', COUNT(*) FROM staff WHERE full_name IS NULL OR email IS NULL OR role IS NULL
UNION ALL
SELECT 'status_log table', 'complaint_id, staff_id, statuses', COUNT(*) FROM status_log WHERE complaint_id IS NULL OR staff_id IS NULL OR old_status IS NULL OR new_status IS NULL
UNION ALL
SELECT 'complaint_feedback table', 'rating, complaint_id', COUNT(*) FROM complaint_feedback WHERE rating IS NULL OR complaint_id IS NULL;


-- ────────────────────────────────────────────────────────────
-- TAB 3: RELATIONAL INTEGRITY — FOREIGN KEY ORPHAN CHECKS
-- ────────────────────────────────────────────────────────────
-- Target: All metrics MUST return 0. Checks if child rows point to non-existent parents.
SELECT 'complaint ➔ citizen' AS relation_path, 'citizen_id' AS joining_key, COUNT(*) AS orphan_count FROM complaint c LEFT JOIN citizen ci ON c.citizen_id = ci.citizen_id WHERE ci.citizen_id IS NULL
UNION ALL
SELECT 'complaint ➔ category', 'category_id', COUNT(*) FROM complaint c LEFT JOIN category ca ON c.category_id = ca.category_id WHERE ca.category_id IS NULL
UNION ALL
SELECT 'complaint ➔ department', 'dept_id', COUNT(*) FROM complaint c LEFT JOIN department d ON c.dept_id = d.dept_id WHERE d.dept_id IS NULL
UNION ALL
SELECT 'status_log ➔ complaint', 'complaint_id', COUNT(*) FROM status_log sl LEFT JOIN complaint c ON sl.complaint_id = c.complaint_id WHERE c.complaint_id IS NULL
UNION ALL
SELECT 'status_log ➔ staff', 'staff_id', COUNT(*) FROM status_log sl LEFT JOIN staff s ON sl.staff_id = s.staff_id WHERE s.staff_id IS NULL
UNION ALL
SELECT 'complaint_feedback ➔ complaint', 'complaint_id', COUNT(*) FROM complaint_feedback cf LEFT JOIN complaint c ON cf.complaint_id = c.complaint_id WHERE c.complaint_id IS NULL
UNION ALL
SELECT 'category ➔ department', 'dept_id', COUNT(*) FROM category cat LEFT JOIN department d ON cat.dept_id = d.dept_id WHERE d.dept_id IS NULL;


-- ────────────────────────────────────────────────────────────
-- TAB 4: GOVERNMENT BUSINESS LOGIC & DOMAIN VALIDATION
-- ────────────────────────────────────────────────────────────
-- Target: All metrics MUST return 0. Validates real-world local gov rules.
SELECT 'Timeline Error' AS rule_violation, 'Resolved timestamp is BEFORE the Filed timestamp' AS rule_description, COUNT(*) AS violation_count FROM complaint WHERE resolved_at IS NOT NULL AND resolved_at < filed_at
UNION ALL
SELECT 'Status Mismatch', 'Active status has resolved_at date OR Resolved status has no date', COUNT(*) FROM complaint WHERE (status IN ('Received', 'In Progress') AND resolved_at IS NOT NULL) OR (status IN ('Resolved', 'Closed') AND resolved_at IS NULL)
UNION ALL
SELECT 'Invalid Identification', 'Pakistani CNIC format length is not exactly 13 digits', COUNT(*) FROM citizen WHERE LENGTH(cnic) != 13
UNION ALL
SELECT 'Feedback Out of Bounds', 'Public satisfaction rating is outside the 1-5 star limit', COUNT(*) FROM complaint_feedback WHERE rating < 1 OR rating > 5;
