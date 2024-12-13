import os
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
from database import add_profile_image_column, calculate_progress, create_tables, connect_user_db,add_injury, get_distinct_injury_types, get_profile_image, get_progress_data, create_user_tables, get_user_by_id, update_profile_image
from recommendations import recommendations 
from werkzeug.utils import secure_filename
import sqlite3
from auth import auth_bp
import config


app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.register_blueprint(auth_bp)


def connect_db():
    return sqlite3.connect('db/database.db')

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
    # add_profile_image_column()
    create_tables() 
    create_user_tables() 
    app.run(debug=True)
