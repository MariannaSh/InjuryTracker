import os

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import calculate_progress, create_tables, add_injury, get_user, get_distinct_injury_types, get_progress_data, create_user_tables
from recommendations import recommendations 
from werkzeug.utils import secure_filename
import sqlite3
from auth import auth_bp
import config


app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.register_blueprint(auth_bp)

# Функция для подключения к базе данных через SQLAlchemy
def connect_db():
    return sqlite3.connect('db/database.db')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home_page():
    if 'username' in session:
        # Получаем список типов травм из базы данных
        injuries = get_distinct_injury_types()
        injuries = [injury[0] for injury in injuries]  # Преобразуем кортежи в список
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
    age = request.form.get('age')
    fitness_level = request.form.get('fitness_level')

    if not injury_type:
        error_message = "Не был выбран тип травмы."
        return render_template('home_page.html', username=session['username'], error=error_message, injuries=get_distinct_injury_types())
    try:
        age = int(age)
        if age < 1 or age > 100:
            error_message = "Вы точно нуждаетесь в рекомендациях?"
            return render_template('home_page.html', username=session['username'], error=error_message, injuries=get_distinct_injury_types())
    except ValueError:
        error_message = "Пожалуйста, введите корректный возраст."
        return render_template('home_page.html', username=session['username'], error=error_message, injuries=get_distinct_injury_types())

    if fitness_level not in ['low', 'medium', 'high']:
        error_message = "Не был выбран уровень физической подготовки."
        return render_template('home_page.html', username=session['username'], error=error_message, injuries=get_distinct_injury_types())

    generated_recommendations = generate_recommendations(injury_type)
    return render_template('recommendations.html', recommendations=generated_recommendations)

# @app.route('/add_progress', methods=['POST'])
# def add_progress_route():
#     # Используем SQLAlchemy для добавления прогресса
#     injury_id = request.form['injury']
#     date = request.form['date']
#     pain_level = request.form['pain_level']
#     exercise_completed = request.form['exercise_completed']
    
#     new_progress = Progress(injury_id=injury_id, date=date, pain_level=pain_level, exercises_completed=exercise_completed)
#     db.session.add(new_progress)
#     db.session.commit()

#     return redirect(url_for('progress'))

@app.route('/progress', methods=['GET', 'POST'])
def progress():
    progress_data = calculate_progress()  # Пожалуйста, уточните логику этой функции, чтобы использовать SQLAlchemy
    if 'username' in session:
        injuries = get_distinct_injury_types()
        injuries = [injury[0] for injury in injuries]  # Преобразуем кортежи в список
        return render_template('progress.html', username=session['username'], injuries=injuries, progress_data=progress_data)
    return render_template('progress.html', progress_data=progress_data)


app.config['UPLOAD_FOLDER'] = 'static/uploads'
# Допустимые расширения файлов
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Функция для проверки допустимых расширений
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/profile')
def user_profile():
    # Получаем имя пользователя и путь к изображению из сессии
    username = session.get('username', 'Guest')
    profile_image = session.get('profile_image', None)
    return render_template('profile.html', username=username, profile_image=profile_image)

@app.route('/update_image', methods=['POST'])
def update_image():
    # Проверяем, есть ли файл в запросе
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Делаем имя файла безопасным
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # Сохраняем файл
            session['profile_image'] = filename  # Сохраняем имя файла в сессии
            return redirect(url_for('user_profile'))  # Перенаправляем на страницу профиля

    return redirect(url_for('user_profile'))  # Если файл не был загружен, возвращаем на профиль



@app.route('/chart')
def chart():
    data = get_progress_data()
    if not data:
        return render_template('chart.html', pain_levels=[], dates=[])

    pain_levels = [row[0] for row in data]  # Уровни боли
    dates = [row[1] for row in data]        # Даты

    return render_template('chart.html', pain_levels=pain_levels, dates=dates)

def generate_recommendations(injury_type):
    return recommendations.get(injury_type.lower(), ["Нет доступных рекомендаций для этой травмы."])

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    create_tables()  # Создаем таблицы для травм
    create_user_tables()  # Создаем таблицы для пользователей
    app.run(debug=True)
