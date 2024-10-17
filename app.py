from flask import Flask, render_template, request, redirect, url_for
from database import create_tables, add_injury, add_progress, get_injuries, get_distinct_injury_types, get_progress_data
from recommendations import recommendations
import sqlite3

app = Flask(__name__)

# Функция для подключения к базе данных
def connect_db():
    return sqlite3.connect('db/database.db')

@app.route('/')
# Главная страница, где отображаются доступные типы травм.
def index():
    injuries = get_distinct_injury_types()
    injuries = [injury[0] for injury in injuries]
    return render_template('index.html', injuries=injuries)

@app.route('/add_injury', methods=['GET', 'POST'])
# Страница для добавления новой травмы в базу данных
def add_injury_route():
    if request.method == 'POST':
        injury_type = request.form['injury_type']
        injury_date = request.form['injury_date']
        add_injury(injury_type, injury_date)
        return redirect(url_for('index'))

    return render_template('add_injury.html')

@app.route('/submit', methods=['POST'])
# Обрабатывает отправку данных о травме и генерирует рекомендации.
def submit():
    injury_type = request.form.get('injury_type')
    if not injury_type:
        return "Не был выбран тип травмы", 400

    generated_recommendations = generate_recommendations(injury_type)
    return render_template('recommendations.html', recommendations=generated_recommendations)

def add_progress(injury_id, date, pain_level, exercise_completed):
    conn = sqlite3.connect('injuries.db')
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO progress (injury_id, date, pain_level, exercise_completed) 
                      VALUES (?, ?, ?, ?)''', (injury_id, date, pain_level, exercise_completed))

    conn.commit()
    conn.close()

@app.route('/add_progress', methods=['POST'])
def add_progress_route():
    # Your existing code for handling the POST request
    injury_id = request.form['injury']
    date = request.form['date']
    pain_level = request.form['pain_level']
    exercise_completed = request.form['exercise_completed']
    
    add_progress(injury_id, date, pain_level, exercise_completed)
    return redirect(url_for('progress'))  # Replace 'some_route' with your actual route


@app.route('/progress', methods=['GET'])
# Страница для записи прогресса восстановления по конкретной травме.
def progress():
    injuries = get_injuries()  
    return render_template('progress.html', injuries=injuries)

@app.route('/chart')
def chart():
    # Получаем данные из базы данных для диаграммы
    data = get_progress_data()
    if not data:
        return render_template('chart.html', pain_levels=[], dates=[])

    # Разделяем данные для использования в диаграмме
    pain_levels = [row[0] for row in data]  # Уровни боли
    dates = [row[1] for row in data]        # Даты

    return render_template('chart.html', pain_levels=pain_levels, dates=dates)

# Генерация рекомендаций на основе типа травмы
def generate_recommendations(injury_type):
    return recommendations.get(injury_type.lower(), ["Нет доступных рекомендаций для этой травмы."])

if __name__ == '__main__':
    create_tables()  # Создаем таблицы при запуске
    app.run(debug=True)
