from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import sqlite3
import os
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'development-secret-key-change-me')

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@vehicleai.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'database', 'vehicle.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}

os.makedirs(os.path.join(BASE_DIR, 'database'), exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    columns = {row[1] for row in cursor.execute('PRAGMA table_info(vehicles)').fetchall()}
    if 'image_path' not in columns:
        cursor.execute('ALTER TABLE vehicles ADD COLUMN image_path TEXT')
    conn.commit()
    conn.close()


init_db()


def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, email, created_at FROM users ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_filter_options():
    conn = get_db_connection()
    cursor = conn.cursor()
    options = {}
    cursor.execute('SELECT DISTINCT type FROM vehicles ORDER BY type')
    options['vehicle_types'] = [row['type'] for row in cursor.fetchall()]
    cursor.execute('SELECT DISTINCT brand FROM vehicles ORDER BY brand')
    options['brands'] = [row['brand'] for row in cursor.fetchall()]
    cursor.execute('SELECT DISTINCT fuel_type FROM vehicles ORDER BY fuel_type')
    options['fuel_types'] = [row['fuel_type'] for row in cursor.fetchall()]
    cursor.execute('SELECT DISTINCT transmission FROM vehicles ORDER BY transmission')
    options['transmissions'] = [row['transmission'] for row in cursor.fetchall()]
    cursor.execute('SELECT DISTINCT body_type FROM vehicles ORDER BY body_type')
    options['body_types'] = [row['body_type'] for row in cursor.fetchall()]
    cursor.execute('SELECT DISTINCT seating_capacity FROM vehicles ORDER BY seating_capacity')
    options['seatings'] = [row['seating_capacity'] for row in cursor.fetchall()]
    cursor.execute('SELECT MIN(price) AS min_price, MAX(price) AS max_price FROM vehicles')
    budget_row = cursor.fetchone()
    options['budget_min_db'] = budget_row['min_price'] if budget_row else None
    options['budget_max_db'] = budget_row['max_price'] if budget_row else None
    conn.close()
    return options


@app.route('/')
def index():
    options = get_filter_options()
    featured = get_featured_vehicles()
    return render_template('index.html', featured=featured, **options)


def get_featured_vehicles(limit=6):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vehicles ORDER BY safety_rating DESC, price ASC LIMIT ?',(limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login', next=request.path))
        return view(*args, **kwargs)
    return wrapped_view


VEHICLE_FIELDS = [
    ('name', 'Name', 'text', True),
    ('brand', 'Brand', 'text', True),
    ('type', 'Vehicle Type', 'text', True),
    ('model_year', 'Model Year', 'number', False),
    ('price', 'Price', 'number', False),
    ('mileage', 'Mileage', 'number', False),
    ('fuel_type', 'Fuel Type', 'text', False),
    ('transmission', 'Transmission', 'text', False),
    ('safety_rating', 'Safety Rating', 'number', False),
    ('engine_cc', 'Engine CC', 'number', False),
    ('seating_capacity', 'Seating Capacity', 'number', False),
    ('power_bhp', 'Power (BHP)', 'number', False),
    ('torque_nm', 'Torque (NM)', 'number', False),
    ('body_type', 'Body Type', 'text', False),
    ('airbags', 'Airbags', 'number', False),
    ('abs', 'ABS', 'text', False),
    ('ground_clearance', 'Ground Clearance', 'number', False),
    ('boot_space', 'Boot Space', 'number', False),
    ('service_cost', 'Service Cost', 'number', False),
    ('insurance_cost', 'Insurance Cost', 'number', False),
]


def vehicle_form_values():
    values = {}
    try:
        for field, _, field_type, required in VEHICLE_FIELDS:
            raw_value = request.form.get(field, '').strip()
            if required and not raw_value:
                raise ValueError(f'{field.replace("_", " ").title()} is required')
            if not raw_value:
                values[field] = None
            elif field_type == 'number':
                values[field] = float(raw_value) if field == 'safety_rating' else int(raw_value)
            else:
                values[field] = raw_value
    except ValueError as error:
        raise ValueError(f'Enter valid vehicle details: {error}') from error
    return values


def save_vehicle_image(file):
    if not file or not file.filename:
        return None
    filename = secure_filename(file.filename)
    extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError('Use a JPG, PNG, WEBP, or GIF image')
    stored_name = f'{secrets.token_hex(12)}.{extension}'
    file.save(os.path.join(UPLOAD_FOLDER, stored_name))
    return f'uploads/{stored_name}'


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if secrets.compare_digest(email, ADMIN_EMAIL) and secrets.compare_digest(password, ADMIN_PASSWORD):
            session['is_admin'] = True
            return redirect(request.args.get('next') or url_for('admin_dashboard'))
        flash('Invalid administrator email or password')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    vehicles = conn.execute('SELECT * FROM vehicles ORDER BY vehicle_id DESC').fetchall()
    users_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    conn.close()
    return render_template('admin_dashboard.html', vehicles=vehicles, users_count=users_count)


@app.route('/admin/vehicles/new', methods=['GET', 'POST'])
@admin_required
def create_vehicle():
    if request.method == 'POST':
        try:
            values = vehicle_form_values()
            values['image_path'] = save_vehicle_image(request.files.get('image'))
        except ValueError as error:
            flash(str(error))
            return render_template('vehicle_form.html', vehicle=request.form, fields=VEHICLE_FIELDS, title='Add Vehicle')
        conn = get_db_connection()
        columns = ', '.join(values)
        placeholders = ', '.join('?' for _ in values)
        conn.execute(f'INSERT INTO vehicles ({columns}) VALUES ({placeholders})', tuple(values.values()))
        conn.commit()
        conn.close()
        flash('Vehicle created successfully')
        return redirect(url_for('admin_dashboard'))
    return render_template('vehicle_form.html', vehicle={}, fields=VEHICLE_FIELDS, title='Add Vehicle')


@app.route('/admin/vehicles/<int:vehicle_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_vehicle(vehicle_id):
    conn = get_db_connection()
    vehicle = conn.execute('SELECT * FROM vehicles WHERE vehicle_id = ?', (vehicle_id,)).fetchone()
    if vehicle is None:
        conn.close()
        flash('Vehicle not found')
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        try:
            values = vehicle_form_values()
            uploaded_image = save_vehicle_image(request.files.get('image'))
            values['image_path'] = uploaded_image or vehicle['image_path']
        except ValueError as error:
            conn.close()
            flash(str(error))
            return render_template('vehicle_form.html', vehicle=request.form, fields=VEHICLE_FIELDS, title='Edit Vehicle')
        assignments = ', '.join(f'{field} = ?' for field in values)
        conn.execute(f'UPDATE vehicles SET {assignments} WHERE vehicle_id = ?', (*values.values(), vehicle_id))
        conn.commit()
        conn.close()
        flash('Vehicle updated successfully')
        return redirect(url_for('admin_dashboard'))
    conn.close()
    return render_template('vehicle_form.html', vehicle=vehicle, fields=VEHICLE_FIELDS, title='Edit Vehicle')


@app.route('/admin/vehicles/<int:vehicle_id>/delete', methods=['POST'])
@admin_required
def delete_vehicle(vehicle_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM vehicles WHERE vehicle_id = ?', (vehicle_id,))
    conn.commit()
    conn.close()
    flash('Vehicle deleted successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password != confirm:
            flash('Passwords do not match')
            return render_template('register.html')

        hashed = generate_password_hash(password)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                           (username, email, hashed))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            flash('Username or email already exists')
            return render_template('register.html')

        return redirect(url_for('users'))

    return render_template('register.html')


@app.route('/users')
def users():
    rows = get_users()
    return render_template('users.html', users=rows)

@app.route('/result', methods=['POST'])
def result():
    vehicle_types = request.form.getlist('vehicle_type')
    brands = request.form.getlist('brand')
    fuel_types = request.form.getlist('fuel_type')
    transmissions = request.form.getlist('transmission')
    seating_capacities = request.form.getlist('seating_capacity')
    body_types = request.form.getlist('body_type')
    budget_min = request.form.get('budget_min')
    budget_max = request.form.get('budget_max')

    query = 'SELECT * FROM vehicles WHERE 1=1'
    params = []

    if vehicle_types:
        placeholders = ','.join('?' for _ in vehicle_types)
        query += f' AND type IN ({placeholders})'
        params.extend(vehicle_types)
    if brands:
        placeholders = ','.join('?' for _ in brands)
        query += f' AND brand IN ({placeholders})'
        params.extend(brands)
    if fuel_types:
        placeholders = ','.join('?' for _ in fuel_types)
        query += f' AND fuel_type IN ({placeholders})'
        params.extend(fuel_types)
    if transmissions:
        placeholders = ','.join('?' for _ in transmissions)
        query += f' AND transmission IN ({placeholders})'
        params.extend(transmissions)
    if seating_capacities:
        placeholders = ','.join('?' for _ in seating_capacities)
        query += f' AND seating_capacity IN ({placeholders})'
        params.extend([int(x) for x in seating_capacities])
    if body_types:
        placeholders = ','.join('?' for _ in body_types)
        query += f' AND body_type IN ({placeholders})'
        params.extend(body_types)
    if budget_min:
        query += ' AND price >= ?'
        params.append(int(budget_min))
    if budget_max:
        query += ' AND price <= ?'
        params.append(int(budget_max))

    query += ' ORDER BY safety_rating DESC, price ASC'

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    vehicles = cursor.fetchall()
    conn.close()

    def format_filter(values):
        return ', '.join(values) if values else 'Any'

    filters = {
        'vehicle_type': format_filter(vehicle_types),
        'brand': format_filter(brands),
        'fuel_type': format_filter(fuel_types),
        'transmission': format_filter(transmissions),
        'seating_capacity': format_filter(seating_capacities),
        'body_type': format_filter(body_types),
        'budget_min': budget_min or 'Any',
        'budget_max': budget_max or 'Any',
    }

    return render_template('result.html', vehicles=vehicles, filters=filters)

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)
