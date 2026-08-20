import os
import sqlite3


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATABASE = os.path.join(BASE_DIR, 'database', 'vehicle.db')


def clean_catalog():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('''
        SELECT vehicle_id
        FROM (
            SELECT vehicle_id,
                   ROW_NUMBER() OVER (
                       PARTITION BY brand, name
                       ORDER BY model_year DESC, safety_rating DESC, price ASC, vehicle_id ASC
                   ) AS row_number
            FROM vehicles
        )
        WHERE row_number > 1
    ''').fetchall()
    conn.executemany('DELETE FROM vehicles WHERE vehicle_id = ?', [(row['vehicle_id'],) for row in rows])
    conn.commit()
    remaining = conn.execute('SELECT COUNT(*) FROM vehicles').fetchone()[0]
    conn.close()
    print(f'Removed {len(rows)} old or duplicate records; {remaining} current model records remain.')


if __name__ == '__main__':
    clean_catalog()