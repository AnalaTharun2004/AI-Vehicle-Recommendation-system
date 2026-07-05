import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'vehicle.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print('tables:')
for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(row)

print('\nschema users:')
for row in cursor.execute("PRAGMA table_info(users)"):
    print(row)

print('\nschema vehicles:')
for row in cursor.execute("PRAGMA table_info(vehicles)"):
    print(row)

print('\nsample vehicles:')
for row in cursor.execute('SELECT name, brand, type, model_year, price, mileage, fuel_type, transmission, safety_rating, seating_capacity FROM vehicles LIMIT 5'):
    print(row)

conn.close()
