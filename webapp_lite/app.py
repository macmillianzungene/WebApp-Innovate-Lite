from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from webapp_lite import db
from webapp_lite.models import User


# Initialize Flask app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance/users.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')
db = SQLAlchemy(app)

# Home route
@app.route('/')
def home():
    return render_template('home.html')


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    due_date = db.Column(db.String(10), nullable=False)  # Add due date
    status = db.Column(db.String(50), nullable=False)    # Add status (e.g., Pending, Completed)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(fullname=fullname, email=email, username=username,
                        password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('registration.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Authenticate user
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('task_manager'))

        flash('Invalid credentials!', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

# Task management route (only accessible when logged in)
@app.route('/tasks', methods=['GET', 'POST'])
def task_manager():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        due_date = request.form['due_date']  # Added due date input
        status = request.form['status']      # Added status input
        description = request.form['description']
        user_id = session['user_id']

        new_task = Task(title=title, description=description, due_date=due_date, status=status, user_id=user_id)
        db.session.add(new_task)
        db.session.commit()

        flash('Task created successfully!', 'success')

    user_id = session['user_id']
    tasks = Task.query.filter_by(user_id=user_id).all()
    return render_template('task_manager.html', tasks=tasks)

# Edit Task route (for updating tasks)
@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get(task_id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.due_date = request.form['due_date']
        task.status = request.form['status']
        task.description = request.form['description']
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('task_manager'))

    return render_template('edit_task.html', task=task)

# Delete Task route
@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('task_manager'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
