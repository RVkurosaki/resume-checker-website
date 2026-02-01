from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('auth.register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"DEBUG: Login attempt for username: {username}")  # Debug log
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session.permanent = True  # Make session permanent
            session['user_id'] = user.id
            session.modified = True  # Explicitly mark session as modified
            print(f"\n{'='*60}")
            print(f"DEBUG /login: Login successful! Set session['user_id'] = {user.id}")
            print(f"DEBUG /login: Session data: {dict(session)}")
            print(f"DEBUG /login: Session.permanent: {session.permanent}")
            print(f"DEBUG /login: Session.modified: {session.modified}")
            print(f"{'='*60}\n")
            return redirect(url_for('dashboard.dashboard'))
        print(f"DEBUG: Login failed for username: {username}")  # Debug log
        flash('Invalid credentials.')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))