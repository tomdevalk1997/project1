import os

from flask import Flask, session
from flask import render_template
#from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Configure session to use filesystem
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#Session(app)

# Set up database
#engine = create_engine(os.getenv("postgres://iutmwfhcnvzjeh:723a5f85dd12d10d4f2c44a58f7781d856595212cca2d1573a176598f4cec44d@ec2-79-125-2-142.eu-west-1.compute.amazonaws.com:5432/dej617ep6sqm62"))
#db = scoped_session(sessionmaker(bind=engine))

#exec('import.py')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/books")
def books():
    return render_template("books.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/books/<int:book_id>")
def book(book_id):
    book = db.execute("SELECT * FROM books WHERE book_id = :book_id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("books.html", message="Unknown book_id")
    return render_template("book.html", book=book)

@app.route("/api/books/<int:book_id>")
def book_api(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :book_id").fetchone()
    if book is None:
        return jsonify({"error": "unknown book_id"}), 404
    return jsonify({
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
        "year": book.year
    })
