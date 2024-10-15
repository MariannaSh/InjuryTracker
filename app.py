from flask import Flask, render_template, request, redirect, url_for
from database import create_tables, add_injury, add_progress, get_injuries, get_distinct_injury_types
from recommendations import recommendations  # Импортируйте ваши рекомендации

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



if __name__ == '__main__':
    create_tables()  # Создаем таблицы при запуске
    app.run(debug=True)
