import pymysql
from werkzeug.security import generate_password_hash

# Match your exact DB_CONFIG settings
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Umerzia600',
    'database': 'lgc_system',
    'cursorclass': pymysql.cursors.DictCursor,
    'charset': 'utf8mb4'
}

def seed_admin_account():
    print("Connecting to your local MySQL lgc_system database...")
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cur:
            # 1. Let's make sure at least one department exists (e.g., ID: 1)
            # This avoids foreign key constraint failures if your department table is empty.
            print("Checking/Ensuring default department...")
            cur.execute("INSERT IGNORE INTO department (dept_id, dept_name) VALUES (1, 'Administration')")
            
            # 2. Check if the admin email already exists in the staff table
            admin_email = "admin@lgc.gov.pk"
            cur.execute("SELECT * FROM staff WHERE email = %s", (admin_email,))
            existing_user = cur.fetchone()
            
            if existing_user:
                print(f"User '{admin_email}' already exists. Overwriting with fresh credentials...")
                new_hash = generate_password_hash("password123")
                cur.execute(
                    "UPDATE staff SET password_hash = %s, is_active = 1, role = 'admin' WHERE email = %s",
                    (new_hash, admin_email)
                )
            else:
                print(f"Creating a completely fresh Admin account for '{admin_email}'...")
                new_hash = generate_password_hash("password123")
                cur.execute(
                    """INSERT INTO staff (dept_id, full_name, email, password_hash, role, is_active) 
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (1, "System Administrator", admin_email, new_hash, "admin", 1)
                )
                
        connection.commit()
        connection.close()
        print("\n🏆 Database successfully seeded!")
        print("---------------------------------------")
        print(f"Email:    {admin_email}")
        print("Password: password123")
        print("---------------------------------------")
        
    except Exception as e:
        print(f"\n❌ Error seeding data: {e}")
        print("Please ensure your local MySQL server is actively running and database 'lgc_system' exists.")

if __name__ == '__main__':
    seed_admin_account()