import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import requests
from database import add_progress, calculate_progress, create_notes_table,  create_tables, connect_user_db,add_injury,  get_distinct_injury_types, get_profile_image, get_progress_data, create_user_tables, get_recommendation, get_user_by_id, update_profile_image

from werkzeug.utils import secure_filename
import sqlite3
from auth import auth_bp
import config


app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.register_blueprint(auth_bp)


def connect_db():
    return sqlite3.connect('db/database.db')


def calculate_bmi(weight_kg, height_cm):
    height_meters = height_cm / 100  # Convert centimeters to meters
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


@app.route('/test',methods=['GET', 'POST'])
def test():
    if request.method == 'POST':

        height_cm = int(request.form['height_cm'])  # Рост в сантиметрах
        weight_kg = int(request.form['weight_kg'])  # Вес в килограммах
        food_item = request.form['food_item']

        # Рассчитываем ИМТ
        bmi = calculate_bmi(weight_kg, height_cm)

        # Fetch Nutrition Info
        nutrition_info = fetch_nutrition_info(food_item)

        return render_template('bmi.html', bmi=bmi, nutrition_info=nutrition_info)

    return render_template('bmi.html', bmi=None, nutrition_info=None)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home_page():
    if 'username' in session:
        injuries = get_distinct_injury_types()
        injuries = [injury[0] for injury in injuries]  
        return render_template('home_page.html', username=session['username'], injuries=injuries)
    return redirect(url_for('index'))

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
    injury_type = request.form.get('injury_type')
    # age = request.form.get('age')
    fitness_level = request.form.get('fitness_level')

    # Валидация данных
    if not injury_type:
        error_message = "Не был выбран тип травмы."
        return render_template('home_page.html', username=session['username'], error=error_message, injuries=get_distinct_injury_types())
    
    # try:
    #     age = int(age)
    #     if age < 1 or age > 100:
    #         error_message = "Вы точно нуждаетесь в рекомендациях?"
    #         return render_template('home_page.html', username=session['username'], error=error_message, injuries=get_distinct_injury_types())
    # except ValueError:
    #     error_message = "Пожалуйста, введите корректный возраст."
    #     return render_template('home_page.html', username=session['username'], error=error_message, injuries=get_distinct_injury_types())

    if fitness_level not in ['low', 'medium', 'high']:
        error_message = "Не был выбран уровень физической подготовки."
        return render_template('home_page.html', username=session['username'], error=error_message, injuries=get_distinct_injury_types())

    # Получение рекомендации с помощью функции get_recommendation
    recommendation = get_recommendation(injury_type, fitness_level)

    # Передаем рекомендацию на страницу recommendations.html
    return render_template('recommendations.html', recommendations=recommendation)




@app.route('/add_progress', methods=['POST'])
def add_progress_route():
    # Your existing code for handling the POST request
    injury_id = request.form['injury_type']
    date = request.form['date']
    pain_level = request.form['pain_level']
    exercise_completed = request.form['exercise_completed']

    add_progress(injury_id, date, pain_level, exercise_completed)
    return redirect(url_for('progress'))

@app.route('/progress', methods=['GET', 'POST'])
def progress():
    progress_data = calculate_progress() 
    if 'username' in session:
        injuries = get_distinct_injury_types()
        injuries = [injury[0] for injury in injuries]  
        return render_template('progress.html', username=session['username'], injuries=injuries, progress_data=progress_data)
    return render_template('progress.html', progress_data=progress_data)


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

            # Обновляем фото в базе
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

@app.route('/chart')
def chart():
    data = get_progress_data()
    if not data:
        return render_template('chart.html', pain_levels=[], dates=[])

    pain_levels = [row[0] for row in data]  
    dates = [row[1] for row in data]       

    return render_template('chart.html', pain_levels=pain_levels, dates=dates)

@app.route('/clear_progress', methods=['POST'])
def clear_progress():
    try:
        conn = sqlite3.connect('injuries.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM progress")  # Очистка всех данных в таблице
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Database cleared!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/recommendations', methods=['GET', 'POST'])
def show_recommendations():
    injury_type = request.form.get('injury_type')  # Тип травмы
    fitness_level = request.form.get('fitness_level')  # Уровень физической активности

    # Получаем рекомендации из базы данных
    recommendations = get_recommendation(injury_type, fitness_level)

    # Передаем данные в шаблон
    return render_template('recommendations.html', recommendations=recommendations)


@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# переделать чтобы в базе хранилось
events = []

@app.route('/get_events', methods=['GET'])
def get_events():
    return jsonify(events)

@app.route('/add_event', methods=['POST'])
def add_event():
    data = request.json
    if 'title' in data and 'date' in data:
        events.append({'title': data['title'], 'start': data['date']})
        return jsonify({'success': True})
    return jsonify({'success': False})
def connect_user_db():
    """Создает соединение с users.db в папке instance."""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'users.db')
    print(f"Подключение к БД: {db_path}")  # Проверяем путь
    return sqlite3.connect(db_path)

@app.route('/add_video', methods=['POST'])
def add_video():
    """Добавляет новое видео в БД."""
    data = request.json
    user_id = session.get("user_id", 1)  # Должен быть реальный ID из сессии
    title = data.get('title')
    link = data.get('link')
    category = data.get('category')

    print(f"Полученные данные: {title}, {link}, {category}")  # Лог для проверки

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
    """Возвращает все сохраненные видео для отображения."""
    conn = connect_user_db()  # Используем правильное подключение к users.db
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, link, category FROM user_notes")
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
    
    # Проверяем, есть ли видео с таким id
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

if __name__ == '__main__':
    create_tables() 
    create_user_tables() 
    app.run(debug=True)
