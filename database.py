import sqlite3

DB_PATH = 'db/database.db'

def create_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    with create_connection() as db:
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS injuries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                injury_type TEXT NOT NULL,
                injury_date TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                injury_id INTEGER,
                date TEXT NOT NULL,
                pain_level INTEGER NOT NULL,
                exercise_completed INTEGER NOT NULL,
                FOREIGN KEY (injury_id) REFERENCES injuries (id)
            )
        ''')
        db.commit()

def add_injury(injury_type, injury_date):
    with create_connection() as db:
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO injuries (injury_type, injury_date) VALUES (?, ?)
        ''', (injury_type, injury_date))
        db.commit()

def add_progress(injury_id, date, pain_level, exercise_completed):
    with create_connection() as db:
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO progress (injury_id, date, pain_level, exercise_completed) VALUES (?, ?, ?, ?)
        ''', (injury_id, date, pain_level, exercise_completed))
        db.commit()

def get_injuries():
    with create_connection() as db:
        cursor = db.cursor()
        cursor.execute('SELECT id, injury_type FROM injuries')
        return cursor.fetchall()

def get_distinct_injury_types():
    with create_connection() as db:
        cursor = db.cursor()
        cursor.execute('SELECT DISTINCT injury_type FROM injuries')
        return cursor.fetchall()


def get_progress_data():
    with create_connection() as db:
        cursor = db.cursor()
        cursor.execute('SELECT pain_level, COUNT(*) FROM progress GROUP BY pain_level')
        return cursor.fetchall()
