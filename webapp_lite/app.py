from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Route for the home page
@app.route('/')
def index():
    return "Welcome to WebApp Innovate Lite!"

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Connect to SQLite and save user details
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (fullname, email, username, password) VALUES (?, ?, ?, ?)', 
                       (fullname, email, username, hashed_password))
        conn.commit()
        conn.close()

        return "Registration successful!"
    return render_template('registration.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to SQLite to check if user exists
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[4], password):  # user[4] refers to the stored hashed password
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Login failed. Please check your username and password."

    return render_template('login.html')

# Route for the dashboard page (after successful login)
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"Welcome, {session['username']}! This is your dashboard."
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)

