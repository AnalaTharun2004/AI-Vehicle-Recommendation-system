from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'database', 'vehicle.db')

os.makedirs(os.path.join(BASE_DIR, 'database'), exist_ok=True)

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
    conn.commit()
    conn.close()


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
