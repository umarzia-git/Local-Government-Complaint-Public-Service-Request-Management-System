-- ============================================================
--  Milestone 4 — DDL Script (CREATE TABLE Statements)
--  Project : Local Government Complaint & Public Service
--            Request Management System
--  Version : 1.0  |  Date : 17 May 2026
--  Commit  : M4: DDL scripts added, EER diagram verified
-- ============================================================


-- ============================================================
-- DATABASE SETUP
-- ============================================================
DROP DATABASE IF EXISTS lgc_system;
CREATE DATABASE lgc_system
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE lgc_system;

-- ============================================================
-- TABLE 1: DEPARTMENT
-- ============================================================
CREATE TABLE department (
    dept_id       INT NOT NULL AUTO_INCREMENT,
    dept_name     VARCHAR(100) NOT NULL,
    head_name     VARCHAR(100) NOT NULL,
    contact_email VARCHAR(100) NULL,
    contact_phone VARCHAR(15) NULL,
    CONSTRAINT pk_department PRIMARY KEY (dept_id),
    CONSTRAINT uq_dept_name UNIQUE (dept_name)
) ENGINE=InnoDB;

-- ============================================================
-- TABLE 2: CATEGORY
-- ============================================================
CREATE TABLE category (
    category_id   INT NOT NULL AUTO_INCREMENT,
    category_name VARCHAR(50) NOT NULL,
    dept_id       INT NOT NULL,
    sla_hours     INT NOT NULL DEFAULT 72,
    description   TEXT NULL,
    CONSTRAINT pk_category PRIMARY KEY (category_id),
    CONSTRAINT uq_category_name UNIQUE (category_name),
    CONSTRAINT fk_category_dept FOREIGN KEY (dept_id)
        REFERENCES department(dept_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_category_dept ON category(dept_id);

-- ============================================================
-- TABLE 3: CITIZEN
-- ============================================================
CREATE TABLE citizen (
    citizen_id    INT NOT NULL AUTO_INCREMENT,
    cnic          VARCHAR(15) NOT NULL,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(100) NOT NULL,
    phone         VARCHAR(15) NOT NULL,
    ward_no       VARCHAR(20) NOT NULL,
    address       TEXT NULL,
    password_hash VARCHAR(255) NOT NULL,
    registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_citizen PRIMARY KEY (citizen_id),
    CONSTRAINT uq_cnic UNIQUE (cnic),
    CONSTRAINT uq_cit_email UNIQUE (email)
) ENGINE=InnoDB;

CREATE INDEX idx_citizen_ward ON citizen(ward_no);

-- ============================================================
-- TABLE 4: STAFF
-- ============================================================
CREATE TABLE staff (
    staff_id      INT NOT NULL AUTO_INCREMENT,
    dept_id       INT NOT NULL,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('staff','admin') NOT NULL DEFAULT 'staff',
    is_active     TINYINT(1) NOT NULL DEFAULT 1,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_staff PRIMARY KEY (staff_id),
    CONSTRAINT uq_staff_email UNIQUE (email),
    CONSTRAINT fk_staff_dept FOREIGN KEY (dept_id)
        REFERENCES department(dept_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_staff_dept ON staff(dept_id);

-- ============================================================
-- TABLE 5: COMPLAINT
-- ============================================================
CREATE TABLE complaint (
    complaint_id     INT NOT NULL AUTO_INCREMENT,
    token            VARCHAR(15) NOT NULL,
    citizen_id       INT NOT NULL,
    category_id      INT NOT NULL,
    dept_id          INT NOT NULL,
    ward_no          VARCHAR(20) NOT NULL,
    description      TEXT NOT NULL,
    photo_path       VARCHAR(255) NULL,
    status           ENUM('Received','In Progress','Resolved','Closed') NOT NULL DEFAULT 'Received',
    priority         ENUM('Normal','High','CRITICAL') NOT NULL DEFAULT 'Normal',
    sla_deadline     DATETIME NULL,
    feedback_pending TINYINT(1) NOT NULL DEFAULT 0,
    filed_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at      DATETIME NULL,
    CONSTRAINT pk_complaint PRIMARY KEY (complaint_id),
    CONSTRAINT uq_token UNIQUE (token),
    CONSTRAINT fk_complaint_cit FOREIGN KEY (citizen_id)
        REFERENCES citizen(citizen_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_complaint_cat FOREIGN KEY (category_id)
        REFERENCES category(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_complaint_dept FOREIGN KEY (dept_id)
        REFERENCES department(dept_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_complaint_citizen ON complaint(citizen_id);
CREATE INDEX idx_complaint_category ON complaint(category_id);
CREATE INDEX idx_complaint_dept ON complaint(dept_id);
CREATE INDEX idx_complaint_ward ON complaint(ward_no);
CREATE INDEX idx_complaint_status ON complaint(status);
CREATE INDEX idx_complaint_filed ON complaint(filed_at);

-- ============================================================
-- TABLE 6: STATUS_LOG
-- ============================================================
CREATE TABLE status_log (
    log_id       INT NOT NULL AUTO_INCREMENT,
    complaint_id INT NOT NULL,
    staff_id     INT NOT NULL,
    old_status   ENUM('Received','In Progress','Resolved','Closed') NOT NULL,
    new_status   ENUM('Received','In Progress','Resolved','Closed') NOT NULL,
    note         TEXT NULL,
    changed_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_status_log PRIMARY KEY (log_id),
    CONSTRAINT fk_log_complaint FOREIGN KEY (complaint_id)
        REFERENCES complaint(complaint_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_log_staff FOREIGN KEY (staff_id)
        REFERENCES staff(staff_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_log_complaint ON status_log(complaint_id);
CREATE INDEX idx_log_staff ON status_log(staff_id);
CREATE INDEX idx_log_changed ON status_log(changed_at);

-- ============================================================
-- TABLE 7: COMPLAINT_FEEDBACK
-- ============================================================
CREATE TABLE complaint_feedback (
    feedback_id  INT NOT NULL AUTO_INCREMENT,
    complaint_id INT NOT NULL,
    citizen_id   INT NOT NULL,
    dept_id      INT NOT NULL,
    rating       TINYINT NOT NULL,
    comments     TEXT NULL,
    submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_feedback PRIMARY KEY (feedback_id),
    CONSTRAINT uq_feedback_compl UNIQUE (complaint_id),
    CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT fk_fb_complaint FOREIGN KEY (complaint_id)
        REFERENCES complaint(complaint_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_fb_citizen FOREIGN KEY (citizen_id)
        REFERENCES citizen(citizen_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_fb_dept FOREIGN KEY (dept_id)
        REFERENCES department(dept_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_fb_dept ON complaint_feedback(dept_id);
CREATE INDEX idx_fb_rating ON complaint_feedback(rating);

-- ============================================================
-- TABLE 8: CHRONIC_ISSUE
-- ============================================================
CREATE TABLE chronic_issue (
    chronic_id      INT NOT NULL AUTO_INCREMENT,
    category_id     INT NOT NULL,
    ward_no         VARCHAR(20) NOT NULL,
    complaint_count INT NOT NULL,
    detected_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_resolved     TINYINT(1) NOT NULL DEFAULT 0,
    resolution_note TEXT NULL,
    CONSTRAINT pk_chronic PRIMARY KEY (chronic_id),
    CONSTRAINT fk_chronic_cat FOREIGN KEY (category_id)
        REFERENCES category(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_chronic_category ON chronic_issue(category_id);
CREATE INDEX idx_chronic_ward ON chronic_issue(ward_no);

-- ============================================================
-- TRIGGER 1: detect recurring complaints
-- Safe version: writes only to chronic_issue, does not update complaint
-- ============================================================
DELIMITER $$

CREATE TRIGGER trg_detect_recurring
AFTER INSERT ON complaint
FOR EACH ROW
BEGIN
    DECLARE v_count INT DEFAULT 0;

    SELECT COUNT(*) INTO v_count
    FROM complaint
    WHERE category_id = NEW.category_id
      AND ward_no = NEW.ward_no
      AND filed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY);

    IF v_count >= 3 AND NOT EXISTS (
        SELECT 1
        FROM chronic_issue
        WHERE category_id = NEW.category_id
          AND ward_no = NEW.ward_no
          AND is_resolved = 0
    ) THEN
        INSERT INTO chronic_issue (category_id, ward_no, complaint_count)
        VALUES (NEW.category_id, NEW.ward_no, v_count);
    END IF;
END$$

DELIMITER ;

-- ============================================================
-- TRIGGER 2: auto-fill resolved_at and feedback flag
-- ============================================================
DELIMITER $$

CREATE TRIGGER trg_feedback_on_resolve
BEFORE UPDATE ON complaint
FOR EACH ROW
BEGIN
    IF NEW.status = 'Resolved' AND OLD.status <> 'Resolved' THEN
        SET NEW.feedback_pending = 1;
        SET NEW.resolved_at = CURRENT_TIMESTAMP;
    END IF;
END$$

DELIMITER ;

-- ============================================================
-- VIEW 1: department KPI
-- ============================================================
CREATE VIEW v_department_kpi AS
SELECT
    d.dept_id,
    d.dept_name,
    COUNT(DISTINCT c.complaint_id) AS total_resolved,
    COUNT(DISTINCT cf.feedback_id) AS total_feedback,
    ROUND(AVG(cf.rating), 2) AS avg_rating,
    SUM(CASE WHEN c.resolved_at <= c.sla_deadline THEN 1 ELSE 0 END) AS resolved_on_time,
    ROUND(
        SUM(CASE WHEN c.resolved_at <= c.sla_deadline THEN 1 ELSE 0 END)
        / NULLIF(COUNT(DISTINCT c.complaint_id), 0) * 100, 1
    ) AS on_time_pct
FROM department d
LEFT JOIN complaint c
    ON c.dept_id = d.dept_id
   AND c.status IN ('Resolved','Closed')
LEFT JOIN complaint_feedback cf
    ON cf.dept_id = d.dept_id
GROUP BY d.dept_id, d.dept_name;

-- ============================================================
-- VIEW 2: ward heatmap
-- ============================================================
CREATE VIEW v_ward_heatmap AS
SELECT
    c.ward_no,
    COUNT(c.complaint_id) AS open_complaints,
    SUM(CASE WHEN NOW() > c.sla_deadline
              AND c.status NOT IN ('Resolved','Closed')
             THEN 1 ELSE 0 END) AS sla_breaches,
    ROUND(COALESCE(AVG(cf.rating), 3), 2) AS avg_satisfaction,
    ROUND(
        (COUNT(c.complaint_id) * 0.40) +
        (SUM(CASE WHEN NOW() > c.sla_deadline
                   AND c.status NOT IN ('Resolved','Closed')
                  THEN 1 ELSE 0 END) * 0.35) +
        ((5 - ROUND(COALESCE(AVG(cf.rating), 3), 2)) * 0.25 * 10)
    , 2) AS risk_score
FROM complaint c
LEFT JOIN complaint_feedback cf
    ON cf.complaint_id = c.complaint_id
WHERE c.filed_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY c.ward_no
ORDER BY risk_score DESC;

-- ============================================================
-- END OF DDL SCRIPT
-- ============================================================
-- Commit Message: M4: DDL scripts added, EER diagram verified
-- ============================================================
