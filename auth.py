# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_bcrypt import Bcrypt
from database import add_user, get_user, get_user_by_id  # Не забудьте импортировать функции работы с пользователями

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Укажите на маршрут входа

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(user_id)  # Реализуйте эту функцию
    if user_data:
        return User(user_data[0], user_data[1])
    return None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        add_user(username, password)  # Добавление пользователя в базу данных
        session['username'] = username  # Сохранение имени пользователя в сессии
        return redirect(url_for('home_page'))  # Перенаправление на домашнюю страницу после регистрации
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and bcrypt.check_password_hash(user[2], password):  # Проверка пароля
            session['username'] = username  # Сохранение имени пользователя в сессии
            return redirect(url_for('home_page'))  # Перенаправление на домашнюю страницу
        else:
            return "Invalid username or password", 401  # Сообщение об ошибке (необязательно)
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

