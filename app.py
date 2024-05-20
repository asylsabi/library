from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          title TEXT,
                          description TEXT,
                          composer TEXT,
                          author TEXT,
                          key TEXT,
                          genre TEXT,
                          pdf_path TEXT)''')
        conn.commit()

@app.before_first_request
def initialize():
    init_db()

# Routes and logic will be added here

if __name__ == "__main__":
    app.run(debug=True)


@app.route('/')
def index():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
    return render_template('index.html', books=books)

@app.route('/book/<int:book_id>')
def book(book_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE id=?", (book_id,))
        book = cursor.fetchone()
    return render_template('book.html', book=book)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        composer = request.form['composer']
        author = request.form['author']
        key = request.form['key']
        genre = request.form['genre']
        pdf = request.files['pdf']

        if pdf:
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf.filename)
            pdf.save(pdf_path)
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books (title, description, composer, author, key, genre, pdf_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (title, description, composer, author, key, genre, pdf.filename))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            composer = request.form['composer']
            author = request.form['author']
            key = request.form['key']
            genre = request.form['genre']
            cursor.execute("UPDATE books SET title=?, description=?, composer=?, author=?, key=?, genre=? WHERE id=?",
                           (title, description, composer, author, key, genre, book_id))
            conn.commit()
            return redirect(url_for('book', book_id=book_id))
        else:
            cursor.execute("SELECT * FROM books WHERE id=?", (book_id,))
            book = cursor.fetchone()
    return render_template('edit_book.html', book=book)


@app.route('/')
def index():
    query = request.args.get('query')
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        if query:
            cursor.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + query + '%',))
        else:
            cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
    return render_template('index.html', books=books)
