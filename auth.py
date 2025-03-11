
from flask import Blueprint, current_app, logging, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_bcrypt import Bcrypt
from database import add_user, get_user, get_user_by_id , connect_user_db 
import logging

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  
logger = logging.getLogger(__name__) 

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(user_id)  
    if user_data:
        return User(user_data[0], user_data[1])
    return None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        add_user(username, password)  
        session['username'] = username  
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('auth.login'))  
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user(username)
        
        if not user:
            flash("User does not exist", "error")
            return redirect(url_for('auth.login'))
        
        if not bcrypt.check_password_hash(user[2], password):
            flash("Invalid password", "error")
            return redirect(url_for('auth.login'))

        session['user_id'] = user[0]
        session['username'] = username
        return redirect(url_for('home_page'))

    return render_template('login.html')

@auth_bp.route('/change_password', methods=['POST'])
def change_password():
    if "user_id" not in session:
        current_app.logger.error("The user is not authorized.") 
        return redirect(url_for("auth.login"))  

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    user_id = session["user_id"]

    if not new_password or len(new_password) < 6:
        current_app.logger.warning("Invalid password.") 
        return "The password must be at least 6 characters long.", 400

    with connect_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        stored_password = cursor.fetchone()

        if not stored_password or not bcrypt.check_password_hash(stored_password[0], current_password):
            current_app.logger.warning("The current password is invalid.")  
            return "The current password is invalid.", 401

        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hashed_password, user_id))
        conn.commit()

    current_app.logger.info("Password successfully updated.")  
    return redirect(url_for("user_profile"))

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

