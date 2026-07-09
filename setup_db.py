"""Create the LGC schema and seed base department data. Safe to run multiple times."""
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ['DB_PASSWORD'],
    'cursorclass': pymysql.cursors.DictCursor,
    'charset': 'utf8mb4',
}
DB_NAME = os.environ.get('DB_NAME', 'lgc_system')

TABLES = {
    'department': """
        CREATE TABLE IF NOT EXISTS department (
            dept_id       INT NOT NULL AUTO_INCREMENT,
            dept_name     VARCHAR(100) NOT NULL,
            head_name     VARCHAR(100) NOT NULL,
            contact_email VARCHAR(100) NULL,
            contact_phone VARCHAR(15) NULL,
            CONSTRAINT pk_department PRIMARY KEY (dept_id),
            CONSTRAINT uq_dept_name UNIQUE (dept_name)
        ) ENGINE=InnoDB
    """,
    'category': """
        CREATE TABLE IF NOT EXISTS category (
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
        ) ENGINE=InnoDB
    """,
    'citizen': """
        CREATE TABLE IF NOT EXISTS citizen (
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
        ) ENGINE=InnoDB
    """,
    'staff': """
        CREATE TABLE IF NOT EXISTS staff (
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
        ) ENGINE=InnoDB
    """,
    'complaint': """
        CREATE TABLE IF NOT EXISTS complaint (
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
        ) ENGINE=InnoDB
    """,
    'status_log': """
        CREATE TABLE IF NOT EXISTS status_log (
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
        ) ENGINE=InnoDB
    """,
    'complaint_feedback': """
        CREATE TABLE IF NOT EXISTS complaint_feedback (
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
        ) ENGINE=InnoDB
    """,
    'chronic_issue': """
        CREATE TABLE IF NOT EXISTS chronic_issue (
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
        ) ENGINE=InnoDB
    """,
}

DEPARTMENTS = [
    ('Water Supply & Sanitation', 'Head of Water & Sanitation', 'water@lgc.gov', '03000000001'),
    ('Roads & Infrastructure', 'Head of Roads & Infrastructure', 'roads@lgc.gov', '03000000002'),
    ('Electricity', 'Head of Electricity', 'electricity@lgc.gov', '03000000003'),
    ('Waste Management', 'Head of Waste Management', 'waste@lgc.gov', '03000000004'),
]


def setup():
    db = pymysql.connect(**DB_CONFIG)
    try:
        with db.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        db.commit()
        db.select_db(DB_NAME)

        with db.cursor() as cur:
            for table_name in ('department', 'category', 'citizen', 'staff',
                                'complaint', 'status_log', 'complaint_feedback', 'chronic_issue'):
                cur.execute(TABLES[table_name])
        db.commit()

        with db.cursor() as cur:
            cur.executemany(
                """INSERT INTO department (dept_name, head_name, contact_email, contact_phone)
                   VALUES (%s,%s,%s,%s)
                   ON DUPLICATE KEY UPDATE head_name=VALUES(head_name)""",
                DEPARTMENTS,
            )
        db.commit()
        print('Database schema created and department data seeded successfully.')
    finally:
        db.close()


if __name__ == '__main__':
    setup()
