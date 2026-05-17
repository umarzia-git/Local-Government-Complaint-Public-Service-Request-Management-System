-- ============================================================
--  Milestone 5 — DML Script (Data Population + Validation)
--  Project : Local Government Complaint & Public Service
--            Request Management System
--  Version : 1.0  |  Date : 17 May 2026
--  Commit  : M5: Data populated, validation queries added



-- ============================================================
-- DATA LOAD SECTION
-- Replace the file paths below with your actual CSV paths.
-- Check secure_file_priv first:
--   SHOW VARIABLES LIKE 'secure_file_priv';
-- ============================================================
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE chronic_issue;
TRUNCATE TABLE complaint_feedback;
TRUNCATE TABLE status_log;
TRUNCATE TABLE complaint;
TRUNCATE TABLE staff;
TRUNCATE TABLE citizen;
TRUNCATE TABLE category;
TRUNCATE TABLE department;
SET FOREIGN_KEY_CHECKS = 1;


USE lgc_system;


-- ============================================================
-- 1) DEPARTMENT
-- ============================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/department.csv'
INTO TABLE department
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(dept_id, dept_name, head_name, contact_email, contact_phone);

-- ============================================================
-- 2) CATEGORY (Fixed column mapping)
-- ============================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/category.csv'
INTO TABLE category
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(category_id, category_name, dept_id, sla_hours); 

-- ============================================================
-- 3) CITIZEN
-- ============================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/citizen.csv'
INTO TABLE citizen
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(citizen_id, cnic, full_name, email, phone, ward_no, address, password_hash, registered_at);

-- ============================================================
-- 4) STAFF
-- ============================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/staff.csv'
INTO TABLE staff
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(staff_id, dept_id, full_name, email, password_hash, role, is_active, created_at);


-- ============================================================
-- 5) COMPLAINT (Fixed to handle empty/NULL datetime values)
-- ============================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/complaint.csv'
INTO TABLE complaint
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(complaint_id, token, citizen_id, category_id, dept_id, ward_no, description, photo_path, status, priority, sla_deadline, feedback_pending, filed_at, @resolved_at_var)
SET resolved_at = IF(@resolved_at_var = '', NULL, @resolved_at_var);

-- ============================================================
-- 6) STATUS_LOG
-- ============================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/status_log.csv'
INTO TABLE status_log
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(log_id, complaint_id, staff_id, old_status, new_status, note, changed_at);

-- ============================================================
-- 7) COMPLAINT_FEEDBACK
-- ============================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/complaint_feedback.csv'
INTO TABLE complaint_feedback
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(feedback_id, complaint_id, citizen_id, dept_id, rating, comments, submitted_at);
-- ============================================================
-- 8) CHRONIC_ISSUE
-- ============================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/chronic_issue.csv'
INTO TABLE chronic_issue
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(chronic_id, category_id, ward_no, complaint_count, detected_at, is_resolved, resolution_note);
/* 


-- ============================================================
-- SAMPLE DATA: DEPARTMENT
-- ============================================================
INSERT INTO department (dept_id, dept_name, head_name, contact_email, contact_phone) VALUES
(1, 'Water & Sanitation', 'Asif Mehmood', 'water@lgc.gov.pk', '0912-345001'),
(2, 'Roads & Infrastructure', 'Tariq Hussain', 'roads@lgc.gov.pk', '0912-345002'),
(3, 'Electricity', 'Nadia Bibi', 'electric@lgc.gov.pk', '0912-345003'),
(4, 'Solid Waste Management', 'Usman Shah', 'waste@lgc.gov.pk', '0912-345004');

-- ============================================================
-- SAMPLE DATA: CATEGORY
-- ============================================================
INSERT INTO category (category_id, category_name, dept_id, sla_hours) VALUES
(1, 'Water Supply Issue', 1, 48),
(2, 'Sewage / Drainage', 1, 72),
(3, 'Road Damage', 2, 96),
(4, 'Illegal Encroachment', 2, 120),
(5, 'Street Light Fault', 3, 24),
(6, 'Transformer Issue', 3, 48),
(7, 'Garbage Collection', 4, 48),
(8, 'Open Drain / Nullah', 4, 72);

-- ============================================================
-- SAMPLE DATA: CITIZEN
-- ============================================================
INSERT INTO citizen (citizen_id, cnic, full_name, email, phone, ward_no, address, password_hash, registered_at) VALUES
(1, '3520178523641', 'Ali Hassan', 'ali.hassan12@gmail.com', '03001234567', 'Ward-5', 'House #12, Hayatabad, Peshawar', SHA2('pass123',256), '2025-09-05 10:22:00'),
(2, '3520145632187', 'Sana Tariq', 'sana.tariq99@yahoo.com', '03111234567', 'Ward-3', 'House #88, Saddar, Peshawar', SHA2('pass123',256), '2025-09-10 14:30:00'),
(3, '3520198765001', 'Bilal Ahmed', 'bilal.ahmed55@gmail.com', '03211234567', 'Ward-7', 'House #200, University Town, Peshawar', SHA2('pass123',256), '2025-09-12 09:15:00'),
(4, '3520132145698', 'Fatima Noor', 'fatima.noor22@hotmail.com', '03451234567', 'Ward-2', 'House #34, Warsak Road, Peshawar', SHA2('pass123',256), '2025-09-18 11:00:00'),
(5, '3520165478921', 'Umar Farooq', 'umar.farooq88@gmail.com', '03321234567', 'Ward-9', 'House #77, Kohat Road, Peshawar', SHA2('pass123',256), '2025-10-01 08:45:00'),
(6, '3520112398745', 'Hina Shah', 'hina.shah33@outlook.com', '03011234567', 'Ward-11', 'House #5, Ring Road, Peshawar', SHA2('pass123',256), '2025-10-05 16:20:00'),
(7, '3520187654321', 'Zubair Khan', 'zubair.khan77@gmail.com', '03141234567', 'Ward-6', 'House #120, Dalazak Road, Peshawar', SHA2('pass123',256), '2025-10-10 12:10:00'),
(8, '3520154321098', 'Amna Bibi', 'amna.bibi44@yahoo.com', '03251234567', 'Ward-4', 'House #9, Bara Road, Peshawar', SHA2('pass123',256), '2025-10-15 07:30:00'),
(9, '3520176543210', 'Kashif Malik', 'kashif.malik66@gmail.com', '03061234567', 'Ward-8', 'House #300, Charsadda Road, Peshawar', SHA2('pass123',256), '2025-10-22 13:45:00'),
(10, '3520123456789', 'Rabia Gul', 'rabia.gul11@hotmail.com', '03151234567', 'Ward-1', 'House #18, Hayatabad Ph-3, Peshawar', SHA2('pass123',256), '2025-11-01 09:00:00'),
(11, '3520109876543', 'Adnan Qureshi', 'adnan.qureshi99@gmail.com', '03411234567', 'Ward-12', 'House #55, Saddar, Peshawar', SHA2('pass123',256), '2025-11-08 15:30:00'),
(12, '3520134567812', 'Sara Hussain', 'sara.hussain88@yahoo.com', '03021234567', 'Ward-5', 'House #88, University Town, Peshawar', SHA2('pass123',256), '2025-11-15 10:00:00'),
(13, '3520156789034', 'Imran Awan', 'imran.awan44@outlook.com', '03161234567', 'Ward-3', 'House #200, Ring Road, Peshawar', SHA2('pass123',256), '2025-12-01 08:00:00'),
(14, '3520178901256', 'Nazia Begum', 'nazia.begum77@gmail.com', '03091234567', 'Ward-7', 'House #34, Warsak Road, Peshawar', SHA2('pass123',256), '2025-12-10 14:00:00'),
(15, '3520190123478', 'Tariq Mehmood', 'tariq.mehmood22@gmail.com', '03481234567', 'Ward-10', 'House #100, Bara Road, Peshawar', SHA2('pass123',256), '2026-01-05 11:30:00');

-- ============================================================
-- SAMPLE DATA: STAFF
-- ============================================================
INSERT INTO staff (staff_id, dept_id, full_name, email, password_hash, role, is_active, created_at) VALUES
(1, 1, 'Admin Water', 'admin.water@lgc.gov.pk', SHA2('admin123',256), 'admin', 1, '2025-09-01 08:00:00'),
(2, 2, 'Admin Roads', 'admin.roads@lgc.gov.pk', SHA2('admin123',256), 'admin', 1, '2025-09-01 08:00:00'),
(3, 3, 'Admin Electric', 'admin.electric@lgc.gov.pk', SHA2('admin123',256), 'admin', 1, '2025-09-01 08:00:00'),
(4, 4, 'Admin Waste', 'admin.waste@lgc.gov.pk', SHA2('admin123',256), 'admin', 1, '2025-09-01 08:00:00'),
(5, 1, 'Raheel Khan', 'raheel.khan@lgc.gov.pk', SHA2('staff123',256), 'staff', 1, '2025-09-03 09:00:00'),
(6, 1, 'Sadia Noor', 'sadia.noor@lgc.gov.pk', SHA2('staff123',256), 'staff', 1, '2025-09-03 09:00:00'),
(7, 2, 'Maryam Bibi', 'maryam.bibi@lgc.gov.pk', SHA2('staff123',256), 'staff', 1, '2025-09-03 09:00:00'),
(8, 2, 'Faisal Shah', 'faisal.shah@lgc.gov.pk', SHA2('staff123',256), 'staff', 1, '2025-09-04 09:00:00'),
(9, 3, 'Asim Raza', 'asim.raza@lgc.gov.pk', SHA2('staff123',256), 'staff', 1, '2025-09-04 09:00:00'),
(10, 4, 'Rukhsana Bibi', 'rukhsana.bibi@lgc.gov.pk', SHA2('staff123',256), 'staff', 1, '2025-09-05 09:00:00');

-- ============================================================
-- SAMPLE DATA: COMPLAINT
-- ============================================================
INSERT INTO complaint (complaint_id, token, citizen_id, category_id, dept_id, ward_no, description, status, priority, sla_deadline, feedback_pending, filed_at) VALUES
(1, 'LGC-2026-00001', 1, 1, 1, 'Ward-5', 'No water supply since 3 days in our street.', 'Resolved', 'Normal', '2025-09-07 10:22:00', 1, '2025-09-05 10:22:00'),
(2, 'LGC-2026-00002', 2, 3, 2, 'Ward-3', 'Large pothole on main road near bazaar.', 'In Progress', 'High', '2025-09-18 14:30:00', 0, '2025-09-14 14:30:00'),
(3, 'LGC-2026-00003', 3, 5, 3, 'Ward-7', 'Street light broken for 2 weeks near school.', 'Resolved', 'Normal', '2025-09-13 09:15:00', 1, '2025-09-12 09:15:00'),
(4, 'LGC-2026-00004', 4, 2, 1, 'Ward-2', 'Nali band ho gayi hai, sewage overflow.', 'Received', 'Normal', '2025-09-24 11:00:00', 0, '2025-09-21 11:00:00'),
(5, 'LGC-2026-00005', 5, 7, 4, 'Ward-9', 'Garbage not collected for 5 days.', 'Closed', 'Normal', '2025-10-03 08:45:00', 1, '2025-10-01 08:45:00'),
(6, 'LGC-2026-00006', 6, 6, 3, 'Ward-11', 'Transformer making loud noise near mosque.', 'In Progress', 'High', '2025-10-07 16:20:00', 0, '2025-10-05 16:20:00'),
(7, 'LGC-2026-00007', 7, 1, 1, 'Ward-5', 'Low water pressure in entire street for a week.', 'Received', 'Normal', '2025-10-12 12:10:00', 0, '2025-10-10 12:10:00'),
(8, 'LGC-2026-00008', 8, 4, 2, 'Ward-4', 'Illegal shop built on footpath blocking road access.', 'Resolved', 'Normal', '2025-10-25 07:30:00', 1, '2025-10-15 07:30:00'),
(9, 'LGC-2026-00009', 9, 8, 4, 'Ward-8', 'Open nullah near houses is dangerous for children.', 'Received', 'CRITICAL', '2025-10-29 13:45:00', 0, '2025-10-22 13:45:00'),
(10, 'LGC-2026-00010', 10, 3, 2, 'Ward-1', 'Road completely broken near hospital.', 'Received', 'High', '2025-11-05 09:00:00', 0, '2025-11-01 09:00:00');

-- ============================================================
-- SAMPLE DATA: STATUS LOG
-- ============================================================
INSERT INTO status_log (log_id, complaint_id, staff_id, old_status, new_status, note, changed_at) VALUES
(1, 1, 5, 'Received', 'In Progress', 'Field team dispatched to location', '2025-09-05 14:00:00'),
(2, 1, 5, 'In Progress', 'Resolved', 'Issue resolved, pipe repaired', '2025-09-06 16:00:00'),
(3, 3, 9, 'Received', 'In Progress', 'Electrician assigned', '2025-09-12 11:00:00'),
(4, 3, 9, 'In Progress', 'Resolved', 'Street light replaced and tested', '2025-09-13 08:00:00'),
(5, 5, 10, 'Received', 'In Progress', 'Garbage truck scheduled', '2025-10-02 09:00:00'),
(6, 5, 10, 'In Progress', 'Resolved', 'Garbage collected and area cleaned', '2025-10-03 07:00:00'),
(7, 5, 10, 'Resolved', 'Closed', 'Complaint closed after citizen confirmation', '2025-10-04 10:00:00'),
(8, 8, 7, 'Received', 'In Progress', 'Notice issued to encroacher', '2025-10-16 09:00:00'),
(9, 8, 7, 'In Progress', 'Resolved', 'Encroachment removed by municipal team', '2025-10-24 14:00:00'),
(10, 2, 8, 'Received', 'In Progress', 'Road repair team assigned', '2025-09-15 10:00:00');

-- ============================================================
-- SAMPLE DATA: FEEDBACK
-- ============================================================
INSERT INTO complaint_feedback
(feedback_id, complaint_id, citizen_id, dept_id, rating, comments, submitted_at)
VALUES
(1, 1, 1, 1, 5, 'Very quick response, issue solved within a day. Thank you!', '2025-09-07 10:00:00'),
(2, 3, 3, 3, 4, 'Good service, light replaced but took 2 days.', '2025-09-14 12:00:00'),
(3, 5, 5, 4, 3, 'Garbage collected but workers were late.', '2025-10-04 14:00:00'),
(4, 8, 8, 2, 4, 'Encroachment removed, satisfied with the action taken.', '2025-10-25 09:00:00');

-- ============================================================
-- SAMPLE DATA: CHRONIC ISSUE
-- ============================================================
INSERT INTO chronic_issue (chronic_id, category_id, ward_no, complaint_count, detected_at, is_resolved, resolution_note) VALUES
(1, 1, 'Ward-5', 5, '2025-10-15 08:00:00', 1, 'Main water supply pipe replaced. Issue resolved permanently.'),
(2, 3, 'Ward-3', 4, '2025-11-20 09:00:00', 0, NULL),
(3, 7, 'Ward-8', 3, '2025-12-10 07:00:00', 0, NULL);*/

-- ============================================================
-- VALIDATION / SAMPLE UPDATES
-- ============================================================
UPDATE complaint
SET status = 'Resolved',
    resolved_at = NOW()
WHERE complaint_id = 2
  AND status = 'In Progress';

UPDATE complaint
SET dept_id = 2,
    category_id = 3
WHERE complaint_id = 4;

UPDATE staff
SET is_active = 0
WHERE staff_id = 10;

UPDATE chronic_issue
SET is_resolved = 1,
    resolution_note = 'Emergency repair carried out by Roads department.'
WHERE chronic_id = 2;

-- ============================================================
-- SAMPLE DELETES
-- ============================================================
DELETE FROM complaint
WHERE token = 'LGC-2026-00010'
  AND status = 'Received';

DELETE FROM complaint_feedback
WHERE feedback_id = 6
  AND citizen_id = 3;

-- ────────────────────────────────────────────────────────────
-- Milestone 5 ends here — see validation_queries.sql next
-- ────────────────────────────────────────────────────────────
-- Commit Message: M5: Data populated, validation queries added
-- ────────────────────────────────────────────────────────────
