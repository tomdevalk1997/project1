import os

from flask import Flask, session
from flask import render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import request
import requests
import json

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    logged_in = False
    return render_template("index.html", logged_in=logged_in)

@app.route("/books", methods=["GET", "POST"])
def books():
    if request.method == "GET":
        logged_in = False
        return render_template("books.html", results_count=0, logged_in=logged_in)
    else:
        search_results = db.execute("SELECT * FROM books WHERE title like '%input%' or author like '%input%' or isbn like '%input%'").fetchall()
        if search_results is None:
            results = "No books found"
            logged_in = False
            return render_template("books.html", results_count=0, logged_in=logged_in)
        results_count = search_results.length()
        logged_in = False
        return render_template("books.html", search_results=search_results, results_count=results_count, logged_in=logged_in)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")

        if db.execute("SELECT * FROM users WHERE email=:email", {"email": email}).rowcount > 0:
            if password == password_confirmation:
                db.execute("INSERT INTO users(name, email, password) VALUES(:name, :email, :password)",
                    {"name": name, "email": email, "password": password})
                db.commit()
                logged_in = False
                return render_template("index.html", logged_in=logged_in)
            else:
                pass
                # passwords don't match
        else:
            pass
            # email already exists with other user

@app.route("/")
def search(input):
    search_results = db.execute("SELECT * FROM books WHERE title like '%input%' or author like '%input%' or isbn like '%input%'").fetchall()
    if search_results is None:
        results = "No books found"
        logged_in = False
        return render_template("books.html", results_count=0, logged_in=logged_in)
    results_count = search_results.length()
    logged_in = False
    return render_template("books.html", search_results=search_results, results_count=results_count, logged_in=logged_in)

@app.route("/books/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    if request.method == "POST":
        review_title = request.form.get(review_title)
        review = request.form.get(review)
        print(review_title)
        print(review)
        date = date.today()
        db.execute("INSERT INTO reviews(book_id, title, message, year) VALUES(:book_id, :title, :message, :date, :user_id)",
        {"book_id": book_id, "title": review_title, "message": review, "date": date, "user_id": user_id})
        db.commit()
    else:
        book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id": book_id}).fetchone()
        if book is None:
            logged_in = False
            return render_template("books.html", message="not found", logged_in=logged_in)

        response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "L4JJxvbz5DQuqwHGe9grw", "isbns": book.isbn})
        response_data = response.json()
        reviews_count = response_data["books"][0]["reviews_count"]
        average_rating = response_data["books"][0]["average_rating"]
        #db.execute("UDATE books(SET average_rating=:average_rating, reviews_count=:reviews_count WHERE id=:book_id), {"book_id": book_id, "average_rating": average_rating, "reviews_count": reviews_count}")
        #db.commit()
        reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchall()
        logged_in = False
        return render_template("book.html", book=book, reviews_count=reviews_count, average_rating=average_rating, reviews=reviews, logged_in=logged_in)

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
