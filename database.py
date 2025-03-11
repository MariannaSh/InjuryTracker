import sqlite3
import os
from flask_bcrypt import Bcrypt

DB_PATH_INJURIES = 'db/database.db'  # База данных для травм
DB_PATH_PROGRESS = 'injuries.db'      # База данных для прогресса нужно удалить

def create_connection_injuries():
    return sqlite3.connect(DB_PATH_INJURIES)

def create_connection_progress():
    return sqlite3.connect(DB_PATH_PROGRESS)

def create_tables():
    # Создание таблицы injuries
    with create_connection_injuries() as db:
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS injuries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            injury_type TEXT NOT NULL,
            injury_date TEXT NOT NULL
        )''')
        db.commit()
        

    # # Создание таблицы progress
    # with create_connection_progress() as db:
    #     cursor = db.cursor()
    #     cursor.execute('''CREATE TABLE IF NOT EXISTS progress (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         injury_id INTEGER,
    #         date TEXT NOT NULL,
    #         pain_level INTEGER NOT NULL,
    #         exercise_completed INTEGER NOT NULL,
    #         FOREIGN KEY (injury_id) REFERENCES injuries (id)
    #     )''')
    #     db.commit()
        

def add_injury(injury_type, injury_date):
    with create_connection_injuries() as db:
        cursor = db.cursor()
        cursor.execute('''INSERT INTO injuries (injury_type, injury_date) VALUES (?, ?)''',
                       (injury_type, injury_date))
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
        return [injury for injury in cursor.fetchall()]
    
def get_recommendation(injury_type, fitness_level):
    with create_connection_injuries() as db:
        cursor = db.cursor()

        # Получаем id для травмы
        cursor.execute('SELECT id FROM injuries WHERE injury_type = ?', (injury_type,))
        injury_id = cursor.fetchone()
        if not injury_id:
            return [{"text": "Тип травмы не найден", "image_url": None, "video_url": None}]
        injury_id = injury_id[0]

        # Получаем id для уровня активности
        cursor.execute('SELECT id FROM activity_levels WHERE activity_level = ?', (fitness_level.lower(),))
        activity_level_id = cursor.fetchone()
        if not activity_level_id:
            return [{"text": f"Уровень активности '{fitness_level}' не найден", "image_url": None, "video_url": None}]
        activity_level_id = activity_level_id[0]

        # Получаем рекомендации
        cursor.execute('''
            SELECT recommendation, image_url, video_url 
            FROM recommendations 
            WHERE injury_id = ? AND activity_level_id = ?
        ''', (injury_id, activity_level_id))
        
        rows = cursor.fetchall()

        recommendations = []
        for row in rows:
            text = row[0].strip() if row[0] else "Текст не найден"
            image_url = row[1] if row[1] else None
            video_url = row[2] if row[2] else None

            recommendations.append({
                "text": text,
                "image_url": image_url,
                "video_url": video_url
            })

        return recommendations if recommendations else [{"text": "No recommendations found.", "image_url": None, "video_url": None}]


def add_progress(user_id, injury_id, date, pain_level, exercise_completed):
    with connect_user_db() as db: 
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO progress (user_id, injury_id, date, pain_level, exercise_completed) 
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, injury_id, date, pain_level, exercise_completed))
        db.commit()


def calculate_progress(user_id):
    with connect_user_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM progress WHERE user_id = ?", (user_id,))
        current_count = cursor.fetchone()[0]

        max_count = 100  
        progress = (current_count / max_count) * 10
        return progress


def get_progress_data(user_id):
    with connect_user_db() as db:
        cursor = db.cursor()
        cursor.execute('''
            SELECT pain_level, date 
            FROM progress 
            WHERE user_id = ?
            ORDER BY date
        ''', (user_id,))
        return cursor.fetchall()



create_tables()

# создание базы users
bcrypt = Bcrypt()

def connect_user_db():
    return sqlite3.connect('instance/users.db')

def create_user_tables():
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
    conn = connect_user_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE username = ?''', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = connect_user_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def show_users():
    with connect_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        for user in users:
            print(user)  

def add_profile_image_column():
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
            print(cursor.fetchall())  
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")

def create_notes_table():
    """Создает таблицу user_notes, если она отсутствует."""
    conn = connect_user_db() 
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user_note(user_id, title, link, category):
    conn = connect_user_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO user_notes (user_id, title, link, category) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, link, category))
        conn.commit()
    except Exception as e:
        print(f"An error occurred while adding note: {e}")
    finally:
        conn.close()

def get_user_notes(user_id):
    conn = connect_user_db()
    cursor = conn.cursor()
    cursor.execute('SELECT title, link, category FROM user_notes WHERE user_id = ?', (user_id,))
    notes = cursor.fetchall()
    conn.close()
    return notes  

def delete_user_note(user_id, title):
    conn = connect_user_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_notes WHERE user_id = ? AND title = ?', (user_id, title))
    conn.commit()
    conn.close()
    print(f"Deleted note '{title}' for user ID {user_id}")

create_notes_table()

def create_events_table():
    conn = connect_user_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def create_progress_table():
    conn = connect_user_db()  
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            injury_id INTEGER,
            date TEXT NOT NULL,
            pain_level INTEGER NOT NULL,
            exercise_completed INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (injury_id) REFERENCES injuries(id)
        )
    ''')
    conn.commit()
    conn.close()
    print("Done")