import sqlite3
import os

# Путь к базам данных
DB_PATH_INJURIES = 'db/database.db'  # База данных для травм
DB_PATH_PROGRESS = 'injuries.db'      # База данных для прогресса

def create_connection_injuries():
    return sqlite3.connect(DB_PATH_INJURIES)

def create_connection_progress():
    return sqlite3.connect(DB_PATH_PROGRESS)

def create_tables():
    """Создает таблицы в обеих базах данных, если они не существуют."""
    # Создание таблицы injuries
    with create_connection_injuries() as db:
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS injuries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            injury_type TEXT NOT NULL,
            injury_date TEXT NOT NULL
        )''')
        db.commit()
        

    # Создание таблицы progress
    with create_connection_progress() as db:
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            injury_id INTEGER,
            date TEXT NOT NULL,
            pain_level INTEGER NOT NULL,
            exercise_completed INTEGER NOT NULL,
            FOREIGN KEY (injury_id) REFERENCES injuries (id)
        )''')
        db.commit()
        

def add_injury(injury_type, injury_date):
    with create_connection_injuries() as db:
        cursor = db.cursor()
        cursor.execute('''INSERT INTO injuries (injury_type, injury_date) VALUES (?, ?)''',
                       (injury_type, injury_date))
        db.commit()

def add_progress(injury_id, date, pain_level, exercise_completed):
    """Добавляет прогресс по травме в базу данных прогресса."""
    with create_connection_progress() as db:
        cursor = db.cursor()
        print(f"Adding progress: injury_id={injury_id}, date={date}, pain_level={pain_level}, exercise_completed={exercise_completed}")
        cursor.execute('''INSERT INTO progress (injury_id, date, pain_level, exercise_completed) 
                          VALUES (?, ?, ?, ?)''', 
                       (injury_id, date, pain_level, exercise_completed))
        db.commit()

def get_injuries():
    with create_connection_injuries() as db:
        cursor = db.cursor()
        cursor.execute('SELECT id, injury_type FROM injuries')
        return cursor.fetchall()

def get_distinct_injury_types():
    with create_connection_injuries() as db:
        cursor = db.cursor()
        cursor.execute('SELECT DISTINCT injury_type FROM injuries')
        return cursor.fetchall()

def get_progress_data():
    with create_connection_progress() as db:
        cursor = db.cursor()
        cursor.execute('''SELECT p.pain_level, p.date 
                          FROM progress p
                          ORDER BY p.date''')  # Здесь нет необходимости соединять с injuries, если данные в progress
        data = cursor.fetchall()
        return data

# Вызовите эту функцию при старте приложения
create_tables()
