from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'library_secret_key_2024'
DB = 'library.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        author TEXT NOT NULL,
        genre TEXT DEFAULT 'General',
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    count = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    if count == 0:
        dummy_books = [
            ('Introduction to Algorithms', 'Thomas H. Cormen', 'Computer Science'),
            ('Python Programming', 'Guido van Rossum', 'Programming'),
            ('Operating System Concepts', 'Abraham Silberschatz', 'Systems'),
            ('Database System Concepts', 'Henry F. Korth', 'Database'),
            ('Computer Networks', 'Andrew S. Tanenbaum', 'Networking'),
            ('Clean Code', 'Robert C. Martin', 'Software Engineering'),
            ('The Pragmatic Programmer', 'David Thomas', 'Software Engineering'),
            ('Design Patterns', 'Gang of Four', 'Software Engineering'),
            ('Artificial Intelligence', 'Stuart Russell', 'AI & ML'),
            ('Deep Learning', 'Ian Goodfellow', 'AI & ML'),
            ('Computer Organization', 'Carl Hamacher', 'Hardware'),
            ('Discrete Mathematics', 'Kenneth H. Rosen', 'Mathematics'),
        ]
        conn.executemany('INSERT INTO books (name, author, genre) VALUES (?, ?, ?)', dummy_books)
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        if role == 'admin' and username == 'admin' and password == 'admin123':
            session['user'] = username
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        elif role == 'user' and username == 'user' and password == 'user123':
            session['user'] = username
            session['role'] = 'user'
            return redirect(url_for('user_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = get_db()
    search = request.args.get('search', '')
    if search:
        books = conn.execute(
            'SELECT * FROM books WHERE name LIKE ? OR author LIKE ? ORDER BY added_date DESC',
            (f'%{search}%', f'%{search}%')
        ).fetchall()
    else:
        books = conn.execute('SELECT * FROM books ORDER BY added_date DESC').fetchall()
    total = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    recent = conn.execute('SELECT * FROM books ORDER BY added_date DESC LIMIT 3').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', books=books, total=total, recent=recent, search=search)

@app.route('/add_book', methods=['POST'])
def add_book():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    name = request.form.get('name')
    author = request.form.get('author')
    genre = request.form.get('genre', 'General')
    if name and author:
        conn = get_db()
        conn.execute('INSERT INTO books (name, author, genre) VALUES (?, ?, ?)', (name, author, genre))
        conn.commit()
        conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/user')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    conn = get_db()
    search = request.args.get('search', '')
    if search:
        books = conn.execute(
            'SELECT * FROM books WHERE name LIKE ? OR author LIKE ? ORDER BY name',
            (f'%{search}%', f'%{search}%')
        ).fetchall()
    else:
        books = conn.execute('SELECT * FROM books ORDER BY name').fetchall()
    total = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    conn.close()
    return render_template('user_dashboard.html', books=books, total=total, search=search)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)