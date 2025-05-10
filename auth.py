from flask import Blueprint, current_app, jsonify, logging, render_template, request, redirect, url_for, flash, session
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

        existing_user = get_user(username)
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for('auth.register'))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return redirect(url_for('auth.register'))

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
        return redirect(url_for('home'))

    return render_template('login.html')

@auth_bp.route('/change_password', methods=['POST'])
def change_password():
    if "user_id" not in session:
        return jsonify({"error": "User is not authorized."}), 403

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    user_id = session["user_id"]

    if not current_password or not new_password:
        return jsonify({"error": "Both current and new passwords are required."}), 400

    if len(new_password) < 6:
        return jsonify({"error": "New password must be at least 6 characters long."}), 400

    with connect_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        stored_password = cursor.fetchone()

        if not stored_password:
            return jsonify({"error": "User not found."}), 404

        if not bcrypt.check_password_hash(stored_password[0], current_password):
            return jsonify({"error": "Invalid current password."}), 401

        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hashed_password, user_id))
        conn.commit()

    return jsonify({"success": True, "message": "Password successfully changed."}), 200


@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

