import sqlite3
import os
from flask_bcrypt import Bcrypt

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

def calculate_progress():
    # Получите количество записей в таблице injuries
    with create_connection_progress() as db:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM progress")
        current_count = cursor.fetchone()[0]  # Получаем количество записей
        
        # Укажите максимальное количество записей, которое вы хотите отслеживать
        max_count = 100  # Например, предполагается, что максимум 100 записей
        
        # Рассчитываем прогресс в процентах
        progress = (current_count / max_count) * 10
        return progress


def get_injuries():
    with create_connection_injuries() as db:
        cursor = db.cursor()
        cursor.execute('SELECT id, injury_type FROM injuries')
        return cursor.fetchall()

def get_distinct_injury_types():
    with create_connection_injuries() as db:
        cursor = db.cursor()
        cursor.execute('SELECT DISTINCT injury_type FROM injuries')
        return [injury for injury in cursor.fetchall()]

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

bcrypt = Bcrypt()

def connect_user_db():
    """Создание соединения с базой данных users.db."""
    return sqlite3.connect('instance/users.db')

def create_user_tables():
    """Создание таблицы пользователей, если она не существует."""
    conn = connect_user_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            profile_image TEXT DEFAULT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    """Добавление нового пользователя в базу данных."""
    conn = connect_user_db()
    cursor = conn.cursor()
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        cursor.execute('''INSERT INTO users (username, password_hash) 
                          VALUES (?, ?)''', (username, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"User {username} already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def get_user(username):
    """Получение пользователя по имени пользователя."""
    conn = connect_user_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE username = ?''', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Получение пользователя по его ID."""
    conn = connect_user_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def show_users():
    """Вывод всех пользователей для проверки данных."""
    with connect_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        for user in users:
            print(user)  

def add_profile_image_column():
    """Добавление столбца profile_image в таблицу users, если он отсутствует."""
    conn = connect_user_db()
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN profile_image TEXT DEFAULT NULL')
        conn.commit()
    except sqlite3.OperationalError:
        print("Колонка 'profile_image' уже существует.")
    finally:
        conn.close()

def update_profile_image(user_id, filename):
    """Обновляет изображение профиля пользователя."""
    conn = connect_user_db()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET profile_image = ? WHERE id = ?', (filename, user_id))
        conn.commit()
        print(f"Profile image for user ID {user_id} updated to {filename}.")
    except Exception as e:
        print(f"An error occurred while updating profile image: {e}")
    finally:
        conn.close()

def get_profile_image(user_id):
    """Возвращает путь к изображению профиля пользователя."""
    conn = connect_user_db()
    cursor = conn.cursor()
    cursor.execute('SELECT profile_image FROM users WHERE id = ?', (user_id,))
    profile_image = cursor.fetchone()
    conn.close()
    return profile_image[0] if profile_image else None


def test_connection():
    try:
        with connect_user_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
            print(cursor.fetchall())  # Убедитесь, что таблица "users" существует
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
