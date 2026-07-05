import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'database', 'vehicle.db')


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def print_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, email, created_at FROM users ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print('No registered users found.')
        return

    print('Registered users:')
    print('ID | Username | Email | Created At')
    print('---|----------|-------|-----------')
    for row in rows:
        print(f"{row['user_id']} | {row['username']} | {row['email']} | {row['created_at']}")


if __name__ == '__main__':
    print_users()
