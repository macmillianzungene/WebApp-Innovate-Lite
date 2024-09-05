from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

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

        # Connect to SQLite and save user details
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (fullname, email, username, password) VALUES (?, ?, ?, ?)', 
                       (fullname, email, username, password))
        conn.commit()
        conn.close()

        return "Registration successful!"
    return render_template('registration.html')

if __name__ == "__main__":
    app.run(debug=True)

