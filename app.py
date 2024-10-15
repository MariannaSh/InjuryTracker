from flask import Flask, render_template, request, redirect, url_for
from database import create_tables, add_injury, add_progress, get_injuries, get_distinct_injury_types, get_progress_data
from recommendations import recommendations  # Импортируйте ваши рекомендации
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

@app.route('/')
def index():
    injuries = get_distinct_injury_types()
    injuries = [injury[0] for injury in injuries]  # Преобразуем кортежи в список
    return render_template('index.html', injuries=injuries)

@app.route('/add_injury', methods=['GET', 'POST'])
def add_injury_route():
    if request.method == 'POST':
        injury_type = request.form['injury_type']
        injury_date = request.form['injury_date']
        add_injury(injury_type, injury_date)
        return redirect(url_for('index'))  # Перенаправляем на главную страницу после добавления

    return render_template('add_injury.html')

@app.route('/submit', methods=['POST'])
def submit():
    injury_type = request.form.get('injury_type')
    if not injury_type:
        return "Не был выбран тип травмы", 400

    generated_recommendations = generate_recommendations(injury_type)
    return render_template('recommendations.html', recommendations=generated_recommendations)

@app.route('/progress', methods=['GET', 'POST'])
def progress():
    if request.method == 'POST':
        injury_id = request.form['injury_id']
        date = request.form['date']
        pain_level = request.form['pain_level']
        exercise_completed = request.form['exercise_completed']

        add_progress(injury_id, date, pain_level, exercise_completed)

        return render_template('progress_success.html')  # Страница успешной записи прогресса

    injuries = get_injuries()
    return render_template('progress.html', injuries=injuries)

def generate_recommendations(injury_type):
    return recommendations.get(injury_type.lower(), ["Нет доступных рекомендаций для этой травмы."])

@app.route('/add_progress', methods=['POST'])
def add_progress_route():
    injury_id = request.form.get('injury_id')
    date = request.form.get('date')
    pain_level = int(request.form.get('pain_level'))
    exercise_completed = int(request.form.get('exercise_completed'))

    # Добавляем данные о прогрессе в базу данных
    add_progress(injury_id, date, pain_level, exercise_completed)
    return redirect(url_for('index'))

@app.route('/chart')
def chart():
    data = get_progress_data()  # Эта функция должна возвращать данные о прогрессе
    if not data:  # Проверка, есть ли данные для построения диаграммы
        return "Нет данных для отображения диаграммы.", 404

    pain_levels = [row[0] for row in data]
    counts = [row[1] for row in data]

    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=pain_levels, autopct='%1.1f%%', startangle=140)
    plt.title('Распределение уровней боли')
    plt.axis('equal')

    # Убедимся, что папка static существует
    if not os.path.exists('static'):
        os.makedirs('static')

    # Сохраняем диаграмму как файл в папку static
    chart_path = 'static/chart.png'
    plt.savefig(chart_path)
    plt.close()

    return render_template('chart.html', chart_url=chart_path)

if __name__ == '__main__':
    create_tables()  # Создаем таблицы при запуске
    app.run(debug=True)
