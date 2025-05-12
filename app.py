from datetime import datetime
from urllib.parse import quote
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
from flask import Flask,flash, jsonify, render_template, request, redirect, url_for, session
import requests
from database import  add_progress, create_connection_injuries, create_injury_history_table,  create_tables, connect_user_db,add_injury, delete_user_injury, generate_daily_rehab_tasks, get_current_rehab_phase,  get_distinct_injury_types, get_injuries_history,  get_profile_image, get_progress_data,  get_recommendation, get_rehab_events, get_rehab_plan, get_user_by_id, get_user_injury, save_user_injury, update_profile_image
from werkzeug.utils import secure_filename
import sqlite3
from auth import auth_bp
import config
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.axes import XValueAxis, YValueAxis
from reportlab.lib import colors
from reportlab.graphics import renderPDF

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.register_blueprint(auth_bp)


def connect_db():
    return sqlite3.connect('db/database.db')


def calculate_bmi(weight_kg, height_cm):
    height_meters = height_cm / 100 
    bmi = weight_kg / height_meters ** 2
    return round(bmi, 1)

def fetch_nutrition_info(food_item):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        'x-app-id': '2b5cce06',
        'x-app-key': 'ad6d3675510d898b655722fe6f104dc1',
        'Content-Type': 'application/json'
    }
    data = {
        "query": food_item
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Unable to fetch nutrition info"}


@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    if request.method == 'POST':
        height_cm = request.form.get('height_cm')
        weight_kg = request.form.get('weight_kg')
        food_item = request.form.get('food_item') 

        if height_cm and weight_kg:
            bmi = calculate_bmi(int(weight_kg), int(height_cm))
        else:
            bmi = None 

        if food_item:
            nutrition_info = fetch_nutrition_info(food_item)
        else:
            nutrition_info = None  

        return render_template('bmi.html', bmi=bmi, nutrition_info=nutrition_info)

    return render_template('bmi.html', bmi=None, nutrition_info=None)

@app.route('/')
def index():
    return render_template('index.html')

from datetime import datetime, timedelta
from database import get_user_injury, get_current_rehab_phase, get_distinct_injury_types, get_progress_data

@app.route("/home")
def home():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user_injury = get_user_injury(user_id)

    if not user_injury:
        return render_template("home_page.html",
                               injuries=get_distinct_injury_types(),
                               user_injury=None)

    injury_type, fitness_level, doctor_confirmed, rehab_start_date = user_injury
    rehab_start = datetime.strptime(rehab_start_date, "%Y-%m-%d").date()
    today = datetime.today().date()

    week_offset = request.args.get("week_offset", 0, type=int)
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    week_dates = [monday + timedelta(days=i) for i in range(7)]
    week_range = f"{week_dates[0].strftime('%b %d')} – {week_dates[-1].strftime('%b %d')}"
    current_date = datetime.today().strftime('%Y-%m-%d')

    with connect_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, completed 
            FROM user_events 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today.strftime('%Y-%m-%d')))
        today_tasks = [{"title": row[0], "completed": bool(row[1])} for row in cursor.fetchall()]

        week = []
        for date in week_dates:
            cursor.execute('''
                SELECT id, title, start, end, completed 
                FROM user_events 
                WHERE user_id = ? AND date = ?
            ''', (user_id, date.strftime('%Y-%m-%d')))
            events = [{
                "id": row[0],
                "title": row[1],
                "start": row[2],
                "end": row[3],
                "completed": bool(row[4])

            } for row in cursor.fetchall()]
            week.append({
                "name": date.strftime("%A"),
                "date": date.strftime("%Y-%m-%d"),
                "events": events
            })
    current_phase, _, total_phases = get_current_rehab_phase(user_id)
    progress_percent = round((current_phase / total_phases) * 100, 1) if current_phase and total_phases else 0

    return render_template("home_page.html",
                           injury_type=injury_type,
                           fitness_level=fitness_level,
                           rehab_start_date=rehab_start_date,
                           current_phase=current_phase,
                           total_phases=total_phases,
                           progress_percent=progress_percent,
                           today_tasks=today_tasks,
                           week=week,
                           week_range=week_range,
                           week_offset=week_offset,
                           user_injury=user_injury,
                           current_date=current_date)



@app.route('/add_injury', methods=['GET', 'POST'])
def add_injury_route():
    if request.method == 'POST':
        injury_type = request.form['injury_type']
        injury_date = request.form['injury_date']
        add_injury(injury_type, injury_date)
        return redirect(url_for('index'))

    return render_template('add_injury.html')

@app.route('/submit', methods=['POST'])
def submit():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    injury_type = request.form['injury_type']
    fitness_level = request.form['fitness_level']
    doctor_confirmed = 1 if 'diagnosis_confirmed' in request.form else 0
    rehab_start_date = request.form['date'] 
    
    save_user_injury(user_id, injury_type, fitness_level, doctor_confirmed, rehab_start_date)
    generate_daily_rehab_tasks(user_id, injury_type, fitness_level, rehab_start_date)
    rehab_events = get_rehab_events(user_id)

    conn = connect_user_db()
    cursor = conn.cursor()
    
    for event in rehab_events:
        cursor.execute('''
            INSERT INTO user_events (user_id, title, date)
            VALUES (?, ?, ?)
        ''', (user_id, event["title"], event["start"]))

    conn.commit()
    conn.close()
    
    recommendation = get_recommendation(injury_type, fitness_level)

    return render_template('recommendations.html', recommendations=recommendation)

from reportlab.graphics.shapes import Rect
import re

@app.route('/complete_rehab', methods=['POST'])
def complete_rehab():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    current = get_user_injury(user_id)
    if current:
        injury_type, fitness_level, doctor_confirmed, rehab_start_date = current
        rehab_end_date = datetime.today().strftime('%Y-%m-%d')

        with connect_user_db() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT date, pain_level
                FROM progress
                WHERE user_id = ?
                ORDER BY date
            ''', (user_id,))
            pain_data = cursor.fetchall()

            os.makedirs('static/reports', exist_ok=True)
            safe_injury_type = re.sub(r'[^a-zA-Z0-9_]', '_', injury_type)
            filename = f"progress_user_{user_id}_{safe_injury_type}_{rehab_start_date}.pdf"
            filepath = os.path.join('static/reports', filename)

            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter

            if pain_data:
                x_values = list(range(len(pain_data)))
                y_values = [row[1] for row in pain_data]
                data = list(zip(x_values, y_values))

                drawing = Drawing(400, 200)
                line = LinePlot()
                line.x = 50
                line.y = 30
                line.height = 125
                line.width = 300
                line.data = [data]
                line.lines[0].strokeColor = colors.HexColor("#0d7a7a")
                line.joinedLines = True

                x_axis = XValueAxis()
                x_axis.setPosition(50, 30, 300)
                x_axis.valueMin = 0
                x_axis.valueMax = max(x_values)
                x_axis.visibleGrid = 0
                x_axis.labelTextFormat = lambda v: pain_data[int(v)][0][-5:] if int(v) < len(pain_data) else ""
                x_axis.labels.angle = 45

                y_axis = YValueAxis()
                y_axis.setPosition(50, 30, 125)
                y_axis.valueMin = 0
                y_axis.valueMax = 10
                y_axis.visibleGrid = 1

                line.xValueAxis = x_axis
                line.yValueAxis = y_axis

                frame = Rect(0, 0, drawing.width, drawing.height)
                frame.strokeColor = colors.black
                frame.strokeWidth = 1
                frame.fillColor = colors.HexColor("#f0f0f0")

                drawing.add(frame)
                drawing.add(line)

                renderPDF.draw(drawing, c, 1.1 * inch, height - 3.3 * inch)

            text_y = height - 3.5 * inch
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1 * inch, text_y, "Rehabilitation Report")

            c.setFont("Helvetica", 12)
            c.drawString(1 * inch, text_y - 0.4 * inch, f"Injury: {injury_type}")
            c.drawString(1 * inch, text_y - 0.7 * inch, f"Start Date: {rehab_start_date}")
            c.drawString(1 * inch, text_y - 1.0 * inch, f"End Date: {rehab_end_date}")
            c.drawString(1 * inch, text_y - 1.3 * inch, f"Sessions: {len(pain_data)}")

            if pain_data:
                initial = pain_data[0][1]
                final = pain_data[-1][1]
                reduction = round(((initial - final) / initial) * 100, 1)
                c.drawString(1 * inch, text_y - 1.6 * inch, f"Initial Pain Level: {initial}")
                c.drawString(1 * inch, text_y - 1.9 * inch, f"Final Pain Level: {final}")
                c.drawString(1 * inch, text_y - 2.2 * inch, f"Pain Reduction: {reduction}%")
            else:
                c.drawString(1 * inch, text_y - 1.6 * inch, "No progress data recorded.")

            c.save()

            cursor.execute('''
                INSERT INTO injury_history (user_id, injury_type, fitness_level, doctor_confirmed, rehab_start_date, rehab_end_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, injury_type, fitness_level, doctor_confirmed, rehab_start_date, rehab_end_date))

            delete_user_injury(user_id)
            cursor.execute("DELETE FROM progress WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM user_events WHERE user_id = ?", (user_id,))
            conn.commit()

    flash("Rehabilitation completed and PDF report saved!", "success")
    return redirect(url_for('home'))


@app.route('/add_progress', methods=['POST'])
def add_progress_route():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Пользователь не авторизован"}), 401

    try:
        injury_id = request.form['injury_type']
        date = request.form['date']
        pain_level = request.form['pain_level']
        exercise_completed = request.form['exercise_completed']

        add_progress(user_id, injury_id, date, pain_level, exercise_completed)

        return jsonify({"success": True, "message": "Прогресс успешно добавлен"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/progress', methods=['GET', 'POST'])
def progress():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    injury_history = get_injuries_history(user_id)
    # Добавляем пути к PDF
    history_with_pdf = []
    for injury in injury_history:
        injury_type, _, _, rehab_start_date, rehab_end_date = injury

        # Преобразование дат в формат '11 May 2025'
        start_dt = datetime.strptime(rehab_start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(rehab_end_date, "%Y-%m-%d")
        formatted_start = start_dt.strftime("%d %b %Y")
        formatted_end = end_dt.strftime("%d %b %Y")

        # Продолжительность
        duration = (end_dt - start_dt).days + 1

        # Имя PDF
        filename = f"progress_user_{user_id}_{injury_type.replace(' ', '_')}_{rehab_start_date}.pdf"
        
        # Добавляем в список для шаблона
        history_with_pdf.append((injury_type, formatted_start, formatted_end, filename, duration))

    progress_data = get_progress_data(user_id)
    injuries = [injury[0] for injury in get_distinct_injury_types()]

    return render_template('progress.html',
                           username=session['username'],
                           injuries=injuries,
                           progress_data=progress_data,
                           injury_history=history_with_pdf)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/upload_profile_image', methods=['POST'])
def upload_profile_image():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            update_profile_image(user_id, filename)
            return redirect(url_for('user_profile'))
    return "Invalid file or no file uploaded", 400

@app.route('/profile')
def user_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = get_user_by_id(user_id)
    if not user:
        return "User not found", 404

    profile_image = get_profile_image(user_id)
    return render_template('profile.html', username=user[1], profile_image=profile_image)


@app.route('/change_username', methods=['POST'])
def change_username():
    print(f"Received data: {request.form}")
    if "user_id" not in session:
        app.logger.error("User is not authorized.")
        return redirect(url_for("auth.login"))  \

    new_username = request.form.get("new_username")
    user_id = session["user_id"]

    if not new_username or len(new_username) < 3:
        app.logger.warning("Invalid username.")
        return "The username must be at least 3 characters long.", 400

    with connect_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (new_username,))
        existing_user = cursor.fetchone()

        if existing_user:
            app.logger.warning(f"The username '{new_username}' is already taken.")
            return "The username is already taken. Please select another one..", 409

        cursor.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, user_id))
        conn.commit()

    with connect_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        updated_username = cursor.fetchone()
        app.logger.info(f"Username has been successfully updated: {updated_username}")

    session["username"] = new_username
    return redirect(url_for("user_profile"))

@app.route('/debug_session')
def debug_session():
    return f"Сессия: {session}"

@app.route('/clear_progress', methods=['POST'])
def clear_progress():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"status": "error", "message": "Пользователь не авторизован"}), 401

        with connect_user_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM progress WHERE user_id = ?", (user_id,))
            conn.commit()

        return jsonify({"status": "success", "message": "Прогресс очищен!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/recommendations', methods=['GET'])
def show_recommendations():
    injury_type = request.args.get('injury_type')  
    fitness_level = request.args.get('fitness_level')  

    if not injury_type or not fitness_level:
        flash("Missing injury type or fitness level!", "error")
        return redirect(url_for('home'))

    recommendations = get_recommendation(injury_type, fitness_level)

    return render_template('recommendations.html', recommendations=recommendations)

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/add_video', methods=['POST'])
def add_video():
    """Добавляет новое видео в БД."""
    data = request.json
    user_id = session.get("user_id", 1)  
    title = data.get('title')
    link = data.get('link')
    category = data.get('category')

    conn = connect_user_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_notes (user_id, title, link, category) VALUES (?, ?, ?, ?)",
        (user_id, title, link, category)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/get_videos")
def get_videos():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Пользователь не авторизован"}), 401

    conn = connect_user_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, link, category FROM user_notes WHERE user_id = ?", (user_id,))
    videos = cursor.fetchall()
    conn.close()

    video_list = [
        {"id": video[0], "title": video[1], "link": video[2], "category": video[3]}
        for video in videos
    ]

    return jsonify({"success": True, "videos": video_list})

@app.route("/delete_video/<int:video_id>", methods=["DELETE"])
def delete_video(video_id):
    conn = connect_user_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM user_notes WHERE id = ?", (video_id,))
    video = cursor.fetchone()

    if video:
        cursor.execute("DELETE FROM user_notes WHERE id = ?", (video_id,))
        conn.commit()
        response = {"success": True, "message": "Видео удалено"}
    else:
        response = {"success": False, "message": "Видео не найдено"}
    
    conn.close()
    return jsonify(response)

@app.route('/log_pain', methods=['POST'])
def log_pain():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    pain_level = request.form.get('pain_level')
    pain_date = request.form.get('pain_date')
    exercise_completed = 1  

    user_injury = get_user_injury(user_id)
    if not user_injury:
        flash("Нет активной травмы для записи прогресса", "error")
        return redirect(url_for('home'))

    injury_type = user_injury[0]

    with create_connection_injuries() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM injuries WHERE injury_type = ?", (injury_type,))
        row = cursor.fetchone()
        if not row:
            flash("Ошибка: тип травмы не найден в базе", "error")
            return redirect(url_for('home'))
        injury_id = row[0]

    add_progress(user_id, injury_id, pain_date, pain_level, exercise_completed)

    flash("Progress saved! You can track it in the Progress section.", "success")
    return redirect(url_for('home'))

@app.route('/log_event_progress', methods=['POST'])
def log_event_progress():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"success": False, "message": "User not authorized"}), 401

        pain_level = request.json.get('pain_level')
        event_id = request.json.get('event_id')
        exercise_completed = request.json.get('exercise_completed')

        add_progress(user_id, event_id, datetime.today().strftime('%Y-%m-%d'), pain_level, exercise_completed)
        flash("Progress saved! You can track it in the Progress section.", "success")
        return jsonify({"success": True, "message": "Progress saved successfully!"})

    except Exception as e:
        flash("An error occurred while logging progress.", "error")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/add_event', methods=['POST'])
def add_event():
    try:
        data = request.json
        title = data['title']
        start = data['start']
        end = data['end']
        repeat_type = data.get('repeat_type', 'none')

        start_datetime = datetime.fromisoformat(start)
        end_datetime = datetime.fromisoformat(end)
        event_date = start_datetime.date()  

        if repeat_type == 'daily':
            for i in range(7):  
                new_start = start_datetime + timedelta(days=i)
                new_end = end_datetime + timedelta(days=i)
                with connect_user_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO user_events (user_id, title, date, start, end, repeat_type)
                                      VALUES (?, ?, ?, ?, ?, ?)''', 
                                   (session['user_id'], title, event_date, new_start, new_end, repeat_type))
                    conn.commit()

        elif repeat_type == 'weekly':
            for i in range(4):  
                new_start = start_datetime + timedelta(weeks=i)
                new_end = end_datetime + timedelta(weeks=i)
                with connect_user_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO user_events (user_id, title, date, start, end, repeat_type)
                                      VALUES (?, ?, ?, ?, ?, ?)''', 
                                   (session['user_id'], title, event_date, new_start, new_end, repeat_type))
                    conn.commit()

        elif repeat_type == 'monthly':
            for i in range(3):  
                new_start = start_datetime.replace(month=start_datetime.month + i)
                new_end = end_datetime.replace(month=end_datetime.month + i)
                with connect_user_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO user_events (user_id, title, date, start, end, repeat_type)
                                      VALUES (?, ?, ?, ?, ?, ?)''', 
                                   (session['user_id'], title, event_date, new_start, new_end, repeat_type))
                    conn.commit()

        else: 
            with connect_user_db() as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO user_events (user_id, title, date, start, end, repeat_type)
                                  VALUES (?, ?, ?, ?, ?, ?)''', 
                               (session['user_id'], title, event_date, start_datetime, end_datetime, repeat_type))
                conn.commit()

        return jsonify({"success": True, "message": "Event added successfully!"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/complete_user_event', methods=['POST'])
def complete_user_event():
    try:
        data = request.json
        event_id = data['event_id']

        with connect_user_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_events SET completed = 1 WHERE id = ?
            ''', (event_id,))
            conn.commit()

        return jsonify({"success": True, "message": "Event marked as completed!"})

    except Exception as e:
        print(f"Error marking event as completed: {e}")
        return jsonify({"success": False, "message": "Error marking event as completed!"}), 500


@app.route('/delete_event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        with connect_user_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM user_events WHERE id = ?
            ''', (event_id,))
            conn.commit()

        return jsonify({"success": True, "message": "Event deleted successfully!"})

    except Exception as e:
        print(f"Error deleting event: {e}")
        return jsonify({"success": False, "message": "Error deleting the event!"}), 500


@app.route('/get_events', methods=['GET'])
def get_events():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "User not authorized"}), 401

    conn = connect_user_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, date, completed FROM user_events WHERE user_id = ?", (user_id,))
    events = [
        {
            "id": e[0], "title": e[1], "start": e[2], "color": "#ff69b4" if e[3] else "#007bff", "completed": bool(e[3])
        }
        for e in cursor.fetchall()
    ]

    conn.close()
    return jsonify({"success": True, "events": events})


@app.route('/rehabilitation_plan')
def show_rehabilitation_plan():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user_injury = get_user_injury(user_id)
    if not user_injury:
        flash("No active rehabilitation plan found.", "warning")
        return redirect(url_for('home'))

    injury_type, fitness_level, _, rehab_start_date = user_injury

    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM injuries WHERE injury_type = ?", (injury_type,))
    injury_id = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM activity_levels WHERE activity_level = ?", (fitness_level,))
    activity_level_id = cursor.fetchone()[0]

    conn.close()

    rehab_plan = get_rehab_plan(injury_id, activity_level_id)

    return render_template('rehabilitation_plan.html', rehab_plan=rehab_plan, injury_type=injury_type)

@app.route('/get_recommendation_for_today', methods=['GET'])
def get_recommendation_for_today():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Пользователь не авторизован"}), 401

    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT rehab_start_date, injury_type, fitness_level FROM user_injuries WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if not result:
        return jsonify({"success": False, "message": "Реабилитация не найдена"}), 404

    rehab_start_date, injury_type, fitness_level = result

    rehab_start_date = datetime.strptime(rehab_start_date, "%Y-%m-%d")
    today_date = datetime.today()
    days_since_start = (today_date - rehab_start_date).days

    cursor.execute("SELECT id FROM injuries WHERE injury_type = ?", (injury_type,))
    injury_id = cursor.fetchone()
    
    cursor.execute("SELECT id FROM activity_levels WHERE activity_level = ?", (fitness_level,))
    activity_level_id = cursor.fetchone()

    if not injury_id or not activity_level_id:
        return jsonify({"success": False, "message": "Данные о травме не найдены"}), 404

    injury_id = injury_id[0]
    activity_level_id = activity_level_id[0]

    cursor.execute('''
        SELECT id, phase, phase_name, duration FROM rehab_phases 
        WHERE injury_id = ? AND activity_level_id = ?
        ORDER BY phase
    ''', (injury_id, activity_level_id))

    rehab_phases = cursor.fetchall()
    
    if not rehab_phases:
        return jsonify({"success": False, "message": "Нет этапов реабилитации"}), 404

    current_phase = None
    days_counter = 0

    for phase_id, phase_number, phase_name, duration in rehab_phases:
        if days_since_start < days_counter + duration:
            current_phase = (phase_number, phase_name)
            break
        days_counter += duration

    if not current_phase:
        return jsonify({"success": False, "message": "Все этапы завершены"}), 404

    phase_number, phase_name = current_phase

    cursor.execute('''
        SELECT recommendation
        FROM recommendations 
        WHERE injury_id = ? AND activity_level_id = ? AND recommendation LIKE ?
    ''', (injury_id, activity_level_id, f"%{phase_name}%"))

    recommendations = cursor.fetchall()
    conn.close()

    if not recommendations:
        return jsonify({"success": False, "message": "Нет рекомендаций для текущего этапа"}), 404

    recommendations_list = [
        {"text": row[0]} for row in recommendations
    ]

    return jsonify({"success": True, "phase": phase_name, "recommendations": recommendations_list})


if __name__ == '__main__':
    create_tables() 
    create_injury_history_table()
    app.run(debug=True)
