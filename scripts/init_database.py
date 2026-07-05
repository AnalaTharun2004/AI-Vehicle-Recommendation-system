import sqlite3
import pandas as pd
import os

DATABASE_PATH = 'database/vehicle.db'

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Users table created")
    
    # Create Vehicles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            type TEXT NOT NULL,
            model_year INTEGER,
            price INTEGER,
            mileage INTEGER,
            fuel_type TEXT,
            transmission TEXT,
            safety_rating REAL,
            engine_cc INTEGER,
            seating_capacity INTEGER,
            power_bhp INTEGER,
            torque_nm INTEGER,
            body_type TEXT,
            airbags INTEGER,
            abs TEXT,
            ground_clearance INTEGER,
            boot_space INTEGER,
            service_cost INTEGER,
            insurance_cost INTEGER
        )
    ''')
    print("✓ Vehicles table created")
    
    # Create User Preferences Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            budget_min INTEGER,
            budget_max INTEGER,
            vehicle_type TEXT,
            fuel_preference TEXT,
            seating_capacity INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    print("✓ User Preferences table created")
    
    # Create Recommendations History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            vehicle_id INTEGER,
            recommended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id)
        )
    ''')
    print("✓ Recommendations table created")
    
    conn.commit()
    conn.close()

def import_vehicle_data():
    """Import vehicle data from CSV to database"""
    df = pd.read_csv('datasets/vehicles.csv')
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Check if vehicles table already has data
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM vehicles')
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Insert data from CSV
        df.to_sql('vehicles', conn, if_exists='append', index=False)
        print(f"✓ Imported {len(df)} vehicle records into database")
    else:
        print(f"ℹ Database already contains {count} vehicle records")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("Initializing Vehicle Recommendation Database...")
    print("-" * 50)
    
    # Create tables
    init_database()
    
    # Import vehicle data
    import_vehicle_data()
    
    print("-" * 50)
    print("✓ Database initialization completed successfully!")
    print(f"✓ Database location: {DATABASE_PATH}")
