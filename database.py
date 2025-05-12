from datetime import datetime, timedelta
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
        CREATE TABLE IF NOT EXISTS users 
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

def create_user_injuries_table():
    with create_connection_injuries() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_injuries (
                user_id INTEGER PRIMARY KEY,
                injury_type TEXT NOT NULL,
                fitness_level TEXT NOT NULL,
                doctor_confirmed BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        conn.commit()

def save_user_injury(user_id, injury_type, fitness_level, doctor_confirmed, rehab_start_date):
    with create_connection_injuries() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_injuries (user_id, injury_type, fitness_level, doctor_confirmed, rehab_start_date)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE 
            SET injury_type = ?, fitness_level = ?, doctor_confirmed = ?, rehab_start_date = ?;
        ''', (user_id, injury_type, fitness_level, doctor_confirmed, rehab_start_date,
              injury_type, fitness_level, doctor_confirmed, rehab_start_date))
        conn.commit()

def get_user_injury(user_id):
    with create_connection_injuries() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT injury_type, fitness_level, doctor_confirmed, rehab_start_date 
            FROM user_injuries 
            WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        if result:
            injury_type = result[0].strip() if result[0] else None
            fitness_level = result[1].strip() if result[1] else None
            return injury_type, fitness_level, result[2], result[3]
        return None

def get_distinct_injury_types():
    with sqlite3.connect('db/database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT injury_type FROM injuries")
        return [row[0] for row in cursor.fetchall()]  
    
def get_all_injuries():
    with create_connection_injuries() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT injury_type FROM injuries')
        return [row[0] for row in cursor.fetchall()]

def delete_user_injury(user_id):
    with create_connection_injuries() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_injuries WHERE user_id = ?', (user_id,))
        conn.commit()

def add_rehab_start_date_column():
    with create_connection_injuries() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('ALTER TABLE user_injuries ADD COLUMN rehab_start_date TEXT')
            conn.commit()
            print("Column 'rehab_start_date' added successfully.")
        except sqlite3.OperationalError:
            print("Column 'rehab_start_date' already exists.")

def create_rehab_phases_table():
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rehab_phases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            injury_id INTEGER NOT NULL,
            phase INTEGER NOT NULL,
            phase_name TEXT NOT NULL,
            duration INTEGER NOT NULL,
            activity_level_id INTEGER NOT NULL,
            FOREIGN KEY (injury_id) REFERENCES injuries(id) ON DELETE CASCADE,
            FOREIGN KEY (activity_level_id) REFERENCES activity_levels(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def get_rehab_plan(injury_id, activity_level_id):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT phase, phase_name, duration 
        FROM rehab_phases 
        WHERE injury_id = ? AND activity_level_id = ?
        ORDER BY phase
    ''', (injury_id, activity_level_id))

    rehab_plan = cursor.fetchall()
    conn.close()

    return rehab_plan

def get_rehab_events(user_id):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT injury_type, fitness_level, rehab_start_date 
        FROM user_injuries 
        WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    if not result:
        return []

    injury_type, fitness_level, rehab_start_date = result
    if not rehab_start_date:
        return []

    injury_type = injury_type.strip()
    fitness_level = fitness_level.strip()

    cursor.execute("SELECT id FROM injuries WHERE injury_type = ?", (injury_type,))
    injury_id_row = cursor.fetchone()
    if not injury_id_row:
        print(f"[ERROR] Injury type '{injury_type}' not found")
        return []
    injury_id = injury_id_row[0]

    cursor.execute("SELECT id FROM activity_levels WHERE activity_level = ?", (fitness_level,))
    activity_level_row = cursor.fetchone()
    if not activity_level_row:
        print(f"[ERROR] Activity level '{fitness_level}' not found")
        return []
    activity_level_id = activity_level_row[0]

    cursor.execute('''
        SELECT phase, phase_name, duration 
        FROM rehab_phases 
        WHERE injury_id = ? AND activity_level_id = ?
        ORDER BY phase
    ''', (injury_id, activity_level_id))
    rehab_phases = cursor.fetchall()
    conn.close()

    if not rehab_phases:
        return []

    start_date = datetime.strptime(rehab_start_date, "%Y-%m-%d")
    events = []
    for phase, phase_name, duration in rehab_phases:
        end_date = start_date + timedelta(days=duration)
        events.append({
            "title": f"{phase_name}",
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        })
        start_date = end_date

    return events

def add_completed_column_user_events():
    with connect_user_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE user_events ADD COLUMN completed INTEGER DEFAULT 0")
            conn.commit()
            print("Column 'completed' added to user_events.")
        except sqlite3.OperationalError:
            print("Column 'completed' already exists.")

def get_current_rehab_phase(user_id):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT rehab_start_date, injury_type, fitness_level 
        FROM user_injuries 
        WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()

    if not result:
        return None, None, None

    rehab_start_date, injury_type, fitness_level = result
    if not rehab_start_date or not injury_type or not fitness_level:
        return None, None, None

    injury_type = injury_type.strip()
    fitness_level = fitness_level.strip()

    rehab_start_date = datetime.strptime(rehab_start_date, "%Y-%m-%d")
    days_since_start = (datetime.today() - rehab_start_date).days

    cursor.execute("SELECT id FROM injuries WHERE injury_type = ?", (injury_type,))
    injury_id_row = cursor.fetchone()
    if not injury_id_row:
        print(f"[ERROR] Injury type '{injury_type}' not found in injuries table")
        return None, None, None
    injury_id = injury_id_row[0]

    cursor.execute("SELECT id FROM activity_levels WHERE activity_level = ?", (fitness_level,))
    activity_level_row = cursor.fetchone()
    if not activity_level_row:
        print(f"[ERROR] Activity level '{fitness_level}' not found in activity_levels table")
        return None, None, None
    activity_level_id = activity_level_row[0]

    cursor.execute('''
        SELECT phase, phase_name, duration 
        FROM rehab_phases 
        WHERE injury_id = ? AND activity_level_id = ?
        ORDER BY phase
    ''', (injury_id, activity_level_id))
    rehab_phases = cursor.fetchall()

    conn.close()

    if not rehab_phases:
        return None, None, None

    current_phase = None
    days_counter = 0

    for phase_number, phase_name, duration in rehab_phases:
        if days_since_start < days_counter + duration:
            current_phase = (phase_number, phase_name)
            break
        days_counter += duration

    if not current_phase:
        return None, None, None

    return current_phase[0], current_phase[1], len(rehab_phases)

def generate_daily_rehab_tasks(user_id, injury_type, fitness_level, start_date):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM injuries WHERE injury_type = ?", (injury_type,))
    injury_id = cursor.fetchone()
    if not injury_id:
        return []
    injury_id = injury_id[0]

    cursor.execute("SELECT id FROM activity_levels WHERE activity_level = ?", (fitness_level.lower(),))
    activity_level_id = cursor.fetchone()
    if not activity_level_id:
        return []
    activity_level_id = activity_level_id[0]

    rehab_plan = get_rehab_plan(injury_id, activity_level_id)  
    all_tasks = []
    current_day = datetime.strptime(start_date, "%Y-%m-%d")

    for phase_number, phase_name, duration in rehab_plan:
        for day in range(duration):
            date = current_day.strftime("%Y-%m-%d")
            title = f"Фаза {phase_number}: {phase_name} — день {day + 1}"

            all_tasks.append((user_id, title, date, injury_id))
            current_day += timedelta(days=1)

    with connect_user_db() as user_conn:
        user_cursor = user_conn.cursor()
        for task in all_tasks:
            user_cursor.execute('''
                INSERT INTO user_events (user_id, title, date, completed, injury_id)
                VALUES (?, ?, ?, 0, ?)
            ''', task)
        user_conn.commit()

    return all_tasks

def create_injury_history_table():
    with connect_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS injury_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                injury_type TEXT NOT NULL,
                fitness_level TEXT NOT NULL,
                doctor_confirmed BOOLEAN NOT NULL,
                rehab_start_date TEXT NOT NULL,
                rehab_end_date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()

def get_injuries_history(user_id):
    with connect_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT injury_type, fitness_level, doctor_confirmed, rehab_start_date, rehab_end_date
            FROM injury_history
            WHERE user_id = ?
            ORDER BY rehab_end_date DESC
        ''', (user_id,))
        return cursor.fetchall()
    

def generate_daily_rehab_tasks(user_id, injury_type, fitness_level, start_date):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM injuries WHERE injury_type = ?", (injury_type,))
    injury_row = cursor.fetchone()
    if not injury_row:
        print("Injury not found")
        return
    injury_id = injury_row[0]

    cursor.execute("SELECT id FROM activity_levels WHERE activity_level = ?", (fitness_level.lower(),))
    level_row = cursor.fetchone()
    if not level_row:
        print("Activity level not found")
        return
    activity_level_id = level_row[0]

    cursor.execute('''
        SELECT id, phase, duration
        FROM rehab_phases
        WHERE injury_id = ? AND activity_level_id = ?
        ORDER BY phase
    ''', (injury_id, activity_level_id))

    rehab_phases = cursor.fetchall()
    conn.close()

    if not rehab_phases:
        print("No rehab phases found")
        return

    current_day = datetime.strptime(start_date, "%Y-%m-%d")
    with connect_user_db() as user_conn:
        user_cursor = user_conn.cursor()
        conn = sqlite3.connect('db/database.db') 
        cursor = conn.cursor()
        user_cursor.execute("DELETE FROM user_events WHERE user_id = ?", (user_id,))
        for phase_id, _, duration in rehab_phases:
            for day_number in range(1, duration + 1):
                date = current_day.strftime("%Y-%m-%d")

                cursor.execute('''
                    SELECT task FROM phase_day_tasks
                    WHERE phase_id = ? AND day_number = ?
                ''', (phase_id, day_number))
                tasks = cursor.fetchall()

                if tasks:
                    for task_row in tasks:
                        user_cursor.execute('''
                            INSERT INTO user_events (user_id, title, date, completed)
                            VALUES (?, ?, ?, 0)
                        ''', (user_id, task_row[0], date))
                else:
                    user_cursor.execute('''
                        INSERT INTO user_events (user_id, title, date, completed)
                        VALUES (?, ?, ?, 0)
                    ''', (user_id, f"[No tasks for Phase ID {phase_id} - Day {day_number}]", date))

                current_day += timedelta(days=1)

        user_conn.commit()
        conn.close()