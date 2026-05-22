from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re, uuid

app = Flask(__name__)
app.secret_key = 'lgc_secret_key_2026'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Umerzia600',
    'database': 'lgc_system',
    'cursorclass': pymysql.cursors.DictCursor,
    'charset': 'utf8mb4'
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

def validate_cnic(cnic):
    # Accept both 35201-1234567-1 (15 chars with dashes) and 3520112345671 (13 digits)
    pattern_dashed = r'^\d{5}-\d{7}-\d{1}$'
    pattern_plain  = r'^\d{13}$'
    return bool(re.match(pattern_dashed, cnic) or re.match(pattern_plain, cnic))

def validate_phone(phone):
    # Must start with 0, be 11 digits
    pattern = r'^0\d{10}$'
    return bool(re.match(pattern, phone))

def validate_email(email):
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))

# ─── HOME ────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ─── CITIZEN REGISTER ────────────────────────────────────────────
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        data = request.form
        errors = []

        cnic      = data.get('cnic','').strip()
        full_name = data.get('full_name','').strip()
        email     = data.get('email','').strip()
        phone     = data.get('phone','').strip()
        ward_no   = data.get('ward_no','').strip()
        address   = data.get('address','').strip()
        password  = data.get('password','').strip()
        confirm   = data.get('confirm_password','').strip()

        if not validate_cnic(cnic):
            errors.append('CNIC must be in format 35201-1234567-1 or 13 digits.')
        if not validate_phone(phone):
            errors.append('Phone must start with 0 and be 11 digits (e.g. 03001234567).')
        if not validate_email(email):
            errors.append('Invalid email address.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if not full_name:
            errors.append('Full name is required.')
        if not ward_no:
            errors.append('Ward number is required.')

        if errors:
            return render_template('register.html', errors=errors, form=data)

        pw_hash = generate_password_hash(password)
        try:
            db = get_db()
            with db.cursor() as cur:
                cur.execute("""INSERT INTO citizen (cnic,full_name,email,phone,ward_no,address,password_hash)
                               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                            (cnic, full_name, email, phone, ward_no, address, pw_hash))
            db.commit()
            db.close()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except pymysql.err.IntegrityError as e:
            msg = str(e)
            if 'uq_cnic' in msg:
                errors.append('This CNIC is already registered.')
            elif 'uq_cit_email' in msg:
                errors.append('This email is already registered.')
            else:
                errors.append('Database error: ' + msg)
            return render_template('register.html', errors=errors, form=data)

    return render_template('register.html', errors=[], form={})

# ─── CITIZEN LOGIN ───────────────────────────────────────────────
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email','').strip()
        password = request.form.get('password','').strip()
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM citizen WHERE email=%s", (email,))
            user = cur.fetchone()
        db.close()
        if user and check_password_hash(user['password_hash'], password):
            session['citizen_id']   = user['citizen_id']
            session['citizen_name'] = user['full_name']
            session['role']         = 'citizen'
            return redirect(url_for('citizen_dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

# ─── STAFF LOGIN ─────────────────────────────────────────────────
@app.route('/staff/login', methods=['GET','POST'])
def staff_login():
    if request.method == 'POST':
        email    = request.form.get('email','').strip()
        password = request.form.get('password','').strip()
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM staff WHERE email=%s AND is_active=1", (email,))
            user = cur.fetchone()
        db.close()
        if user and check_password_hash(user['password_hash'], password):
            session['staff_id']   = user['staff_id']
            session['staff_name'] = user['full_name']
            session['staff_role'] = user['role']
            session['dept_id']    = user['dept_id']
            session['role']       = user['role']
            return redirect(url_for('admin_dashboard') if user['role']=='admin' else url_for('staff_dashboard'))
        flash('Invalid credentials or account inactive.', 'danger')
    return render_template('staff_login.html')

# ─── LOGOUT ──────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ─── CITIZEN DASHBOARD ───────────────────────────────────────────
@app.route('/citizen/dashboard')
def citizen_dashboard():
    if session.get('role') != 'citizen':
        return redirect(url_for('login'))
    cid = session['citizen_id']
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT c.*, cat.category_name, d.dept_name
                       FROM complaint c
                       JOIN category cat ON c.category_id=cat.category_id
                       JOIN department d ON c.dept_id=d.dept_id
                       WHERE c.citizen_id=%s ORDER BY c.filed_at DESC""", (cid,))
        complaints = cur.fetchall()
        cur.execute("SELECT * FROM citizen WHERE citizen_id=%s", (cid,))
        citizen = cur.fetchone()
    db.close()
    stats = {
        'total':      len(complaints),
        'received':   sum(1 for c in complaints if c['status']=='Received'),
        'in_progress':sum(1 for c in complaints if c['status']=='In Progress'),
        'resolved':   sum(1 for c in complaints if c['status'] in ('Resolved','Closed')),
    }
    return render_template('citizen_dashboard.html', complaints=complaints, citizen=citizen, stats=stats)

# ─── FILE COMPLAINT ──────────────────────────────────────────────
@app.route('/citizen/complaint/new', methods=['GET','POST'])
def new_complaint():
    if session.get('role') != 'citizen':
        return redirect(url_for('login'))
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM category ORDER BY category_name")
        categories = cur.fetchall()
        cur.execute("SELECT * FROM department ORDER BY dept_name")
        departments = cur.fetchall()
        cur.execute("SELECT * FROM citizen WHERE citizen_id=%s", (session['citizen_id'],))
        citizen = cur.fetchone()
    db.close()

    if request.method == 'POST':
        category_id = request.form.get('category_id')
        dept_id     = request.form.get('dept_id')
        ward_no     = request.form.get('ward_no','').strip()
        description = request.form.get('description','').strip()
        errors = []
        if not category_id: errors.append('Please select a category.')
        if not dept_id:     errors.append('Please select a department.')
        if not ward_no:     errors.append('Ward number is required.')
        if len(description) < 20: errors.append('Description must be at least 20 characters.')
        if errors:
            return render_template('new_complaint.html', categories=categories,
                                   departments=departments, errors=errors, form=request.form, citizen=citizen)
        token = 'LGC-' + datetime.now().strftime('%Y') + '-' + str(uuid.uuid4())[:5].upper()
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""SELECT sla_hours FROM category WHERE category_id=%s""", (category_id,))
            cat = cur.fetchone()
            sla_hours = cat['sla_hours'] if cat else 72
            cur.execute("""INSERT INTO complaint (token,citizen_id,category_id,dept_id,ward_no,description,sla_deadline)
                           VALUES (%s,%s,%s,%s,%s,%s, DATE_ADD(NOW(), INTERVAL %s HOUR))""",
                        (token, session['citizen_id'], category_id, dept_id, ward_no, description, sla_hours))
        db.commit()
        db.close()
        flash(f'Complaint filed! Your token is {token}', 'success')
        return redirect(url_for('citizen_dashboard'))

    return render_template('new_complaint.html', categories=categories,
                           departments=departments, errors=[], form={}, citizen=citizen)

# ─── TRACK COMPLAINT ─────────────────────────────────────────────
@app.route('/citizen/complaint/<int:complaint_id>')
def view_complaint(complaint_id):
    if session.get('role') != 'citizen':
        return redirect(url_for('login'))
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT c.*, cat.category_name, d.dept_name, cat.sla_hours
                       FROM complaint c
                       JOIN category cat ON c.category_id=cat.category_id
                       JOIN department d ON c.dept_id=d.dept_id
                       WHERE c.complaint_id=%s AND c.citizen_id=%s""",
                    (complaint_id, session['citizen_id']))
        complaint = cur.fetchone()
        if not complaint:
            db.close()
            flash('Complaint not found.','danger')
            return redirect(url_for('citizen_dashboard'))
        cur.execute("""SELECT sl.*, s.full_name as staff_name FROM status_log sl
                       JOIN staff s ON sl.staff_id=s.staff_id
                       WHERE sl.complaint_id=%s ORDER BY sl.changed_at""", (complaint_id,))
        logs = cur.fetchall()
        cur.execute("SELECT * FROM complaint_feedback WHERE complaint_id=%s", (complaint_id,))
        feedback = cur.fetchone()
    db.close()
    return render_template('view_complaint.html', complaint=complaint, logs=logs, feedback=feedback)

# ─── SUBMIT FEEDBACK ─────────────────────────────────────────────
@app.route('/citizen/feedback/<int:complaint_id>', methods=['POST'])
def submit_feedback(complaint_id):
    if session.get('role') != 'citizen':
        return redirect(url_for('login'))
    rating   = int(request.form.get('rating', 0))
    comments = request.form.get('comments','').strip()
    if not (1 <= rating <= 5):
        flash('Rating must be between 1 and 5.', 'danger')
        return redirect(url_for('view_complaint', complaint_id=complaint_id))
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT dept_id FROM complaint WHERE complaint_id=%s", (complaint_id,))
        c = cur.fetchone()
        cur.execute("""INSERT INTO complaint_feedback (complaint_id,citizen_id,dept_id,rating,comments)
                       VALUES (%s,%s,%s,%s,%s)""",
                    (complaint_id, session['citizen_id'], c['dept_id'], rating, comments))
        cur.execute("UPDATE complaint SET feedback_pending=0 WHERE complaint_id=%s", (complaint_id,))
    db.commit()
    db.close()
    flash('Feedback submitted. Thank you!', 'success')
    return redirect(url_for('view_complaint', complaint_id=complaint_id))

# ─── STAFF DASHBOARD ─────────────────────────────────────────────
@app.route('/staff/dashboard')
def staff_dashboard():
    if session.get('role') not in ('staff','admin'):
        return redirect(url_for('staff_login'))
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT c.*, cat.category_name, d.dept_name, cit.full_name as citizen_name
                       FROM complaint c
                       JOIN category cat ON c.category_id=cat.category_id
                       JOIN department d ON c.dept_id=d.dept_id
                       JOIN citizen cit ON c.citizen_id=cit.citizen_id
                       WHERE c.dept_id=%s ORDER BY c.filed_at DESC LIMIT 50""",
                    (session['dept_id'],))
        complaints = cur.fetchall()
    db.close()
    stats = {
        'total':      len(complaints),
        'received':   sum(1 for c in complaints if c['status']=='Received'),
        'in_progress':sum(1 for c in complaints if c['status']=='In Progress'),
        'resolved':   sum(1 for c in complaints if c['status'] in ('Resolved','Closed')),
    }
    return render_template('staff_dashboard.html', complaints=complaints, stats=stats)

# ─── UPDATE STATUS ───────────────────────────────────────────────
@app.route('/staff/complaint/<int:complaint_id>/update', methods=['POST'])
def update_status(complaint_id):
    if session.get('role') not in ('staff','admin'):
        return redirect(url_for('staff_login'))
    new_status = request.form.get('new_status')
    note       = request.form.get('note','').strip()
    valid = ('Received','In Progress','Resolved','Closed')
    if new_status not in valid:
        flash('Invalid status.', 'danger')
        return redirect(url_for('staff_dashboard'))
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT status FROM complaint WHERE complaint_id=%s", (complaint_id,))
        row = cur.fetchone()
        if row:
            old_status = row['status']
            cur.execute("UPDATE complaint SET status=%s WHERE complaint_id=%s", (new_status, complaint_id))
            cur.execute("""INSERT INTO status_log (complaint_id,staff_id,old_status,new_status,note)
                           VALUES (%s,%s,%s,%s,%s)""",
                        (complaint_id, session['staff_id'], old_status, new_status, note))
    db.commit()
    db.close()
    flash('Status updated successfully.', 'success')
    return redirect(url_for('staff_dashboard'))

# ─── ADMIN DASHBOARD ─────────────────────────────────────────────
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('staff_login'))
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM v_department_kpi")
        dept_kpi = cur.fetchall()
        cur.execute("SELECT * FROM v_ward_heatmap ORDER BY risk_score DESC LIMIT 10")
        ward_heatmap = cur.fetchall()
        cur.execute("""SELECT c.*, cat.category_name, d.dept_name, cit.full_name as citizen_name
                       FROM complaint c
                       JOIN category cat ON c.category_id=cat.category_id
                       JOIN department d ON c.dept_id=d.dept_id
                       JOIN citizen cit ON c.citizen_id=cit.citizen_id
                       ORDER BY c.filed_at DESC LIMIT 100""")
        complaints = cur.fetchall()
        cur.execute("SELECT COUNT(*) as cnt FROM citizen")
        citizen_count = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) as cnt FROM complaint WHERE status NOT IN ('Resolved','Closed')")
        open_count = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) as cnt FROM chronic_issue WHERE is_resolved=0")
        chronic_count = cur.fetchone()['cnt']
        cur.execute("SELECT ROUND(AVG(rating),2) as avg FROM complaint_feedback")
        avg_rating = cur.fetchone()['avg'] or 0
        cur.execute("""SELECT ci.*, cat.category_name FROM chronic_issue ci
                       JOIN category cat ON ci.category_id=cat.category_id
                       WHERE ci.is_resolved=0 ORDER BY ci.detected_at DESC""")
        chronic_issues = cur.fetchall()
    db.close()
    return render_template('admin_dashboard.html',
                           dept_kpi=dept_kpi, ward_heatmap=ward_heatmap,
                           complaints=complaints, citizen_count=citizen_count,
                           open_count=open_count, chronic_count=chronic_count,
                           avg_rating=avg_rating, chronic_issues=chronic_issues)

# ─── ADMIN: MANAGE STAFF ─────────────────────────────────────────
@app.route('/admin/staff', methods=['GET','POST'])
def manage_staff():
    if session.get('role') != 'admin':
        return redirect(url_for('staff_login'))
    db = get_db()
    errors = []
    if request.method == 'POST':
        full_name = request.form.get('full_name','').strip()
        email     = request.form.get('email','').strip()
        password  = request.form.get('password','').strip()
        role      = request.form.get('role','staff')
        dept_id   = request.form.get('dept_id')
        if not validate_email(email): errors.append('Invalid email.')
        if len(password) < 6:         errors.append('Password min 6 chars.')
        if not errors:
            pw_hash = generate_password_hash(password)
            try:
                with db.cursor() as cur:
                    cur.execute("""INSERT INTO staff (dept_id,full_name,email,password_hash,role)
                                   VALUES (%s,%s,%s,%s,%s)""",
                                (dept_id, full_name, email, pw_hash, role))
                db.commit()
                flash('Staff member added.', 'success')
            except pymysql.err.IntegrityError:
                errors.append('Email already exists.')
    with db.cursor() as cur:
        cur.execute("""SELECT s.*, d.dept_name FROM staff s JOIN department d ON s.dept_id=d.dept_id ORDER BY s.created_at DESC""")
        staff_list = cur.fetchall()
        cur.execute("SELECT * FROM department ORDER BY dept_name")
        departments = cur.fetchall()
    db.close()
    return render_template('manage_staff.html', staff_list=staff_list,
                           departments=departments, errors=errors)

# ─── API: GET DEPT FOR CATEGORY ──────────────────────────────────
@app.route('/api/category/<int:cat_id>/dept')
def api_category_dept(cat_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT dept_id FROM category WHERE category_id=%s", (cat_id,))
        row = cur.fetchone()
    db.close()
    return jsonify(row or {})

# ─── TRACK BY TOKEN (PUBLIC) ─────────────────────────────────────
@app.route('/track', methods=['GET','POST'])
def track():
    complaint = None
    logs = []
    if request.method == 'POST':
        token = request.form.get('token','').strip()
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""SELECT c.*, cat.category_name, d.dept_name
                           FROM complaint c
                           JOIN category cat ON c.category_id=cat.category_id
                           JOIN department d ON c.dept_id=d.dept_id
                           WHERE c.token=%s""", (token,))
            complaint = cur.fetchone()
            if complaint:
                cur.execute("""SELECT sl.*, s.full_name as staff_name FROM status_log sl
                               JOIN staff s ON sl.staff_id=s.staff_id
                               WHERE sl.complaint_id=%s ORDER BY sl.changed_at""",
                            (complaint['complaint_id'],))
                logs = cur.fetchall()
        db.close()
        if not complaint:
            flash('No complaint found with that token.', 'warning')
    return render_template('track.html', complaint=complaint, logs=logs)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
