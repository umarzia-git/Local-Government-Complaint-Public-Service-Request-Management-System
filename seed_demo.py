"""Seed the database with clean demo accounts for local development/portfolio use."""
import os
import pymysql
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ['DB_PASSWORD'],
    'database': os.environ.get('DB_NAME', 'lgc_system'),
    'cursorclass': pymysql.cursors.DictCursor,
    'charset': 'utf8mb4',
}


def seed():
    db = pymysql.connect(**DB_CONFIG)
    try:
        with db.cursor() as cur:
            cur.execute("SELECT dept_id FROM department ORDER BY dept_id LIMIT 1")
            dept = cur.fetchone()
            if dept:
                dept_id = dept['dept_id']
            else:
                cur.execute("""INSERT INTO department (dept_name, head_name, contact_email, contact_phone)
                               VALUES ('General Services', 'Demo Head', 'dept@demo.com', '03000000000')""")
                dept_id = cur.lastrowid

            cur.execute("""INSERT INTO citizen (cnic, full_name, email, phone, ward_no, address, password_hash)
                           VALUES (%s,%s,%s,%s,%s,%s,%s)
                           ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash)""",
                        ('35201-1234567-1', 'Demo Citizen', 'citizen@demo.com', '03001234567',
                         '1', 'Demo Address, Demo City', generate_password_hash('demo123')))

            cur.execute("""INSERT INTO staff (dept_id, full_name, email, password_hash, role)
                           VALUES (%s,%s,%s,%s,'staff')
                           ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash)""",
                        (dept_id, 'Demo Staff', 'staff@demo.com', generate_password_hash('demo123')))

            cur.execute("""INSERT INTO staff (dept_id, full_name, email, password_hash, role)
                           VALUES (%s,%s,%s,%s,'admin')
                           ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash)""",
                        (dept_id, 'Admin User', 'admin@demo.com', generate_password_hash('admin123')))
        db.commit()
        print('Demo data seeded successfully.')
    finally:
        db.close()


if __name__ == '__main__':
    seed()
