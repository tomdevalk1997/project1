import os
from flask import Flask, session
from flask import url_for
from flask import render_template
from flask import redirect
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

logged_in = False

@app.route("/")
def index():
    return render_template("index.html", logged_in=logged_in, alert_message="")

@app.route("/books", methods=["GET", "POST"])
def books():
    if request.method == "GET":
        return render_template("books.html", results_count=0, logged_in=logged_in)
    else:
        search_results = db.execute("SELECT * FROM books WHERE title like '%input%' or author like '%input%' or isbn like '%input%'").fetchall()
        if search_results is None:
            print("No books found")
            return render_template("books.html", results_count=0, logged_in=logged_in)
        return render_template("books.html", search_results=search_results, results_count=1, logged_in=logged_in)

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
                print("Registration succesful")
                return render_template("index.html", logged_in=logged_in)
            else:
                print("Passwords need to be the same to register.")
        else:
            print("Email address is already present in the database. Log in or register a different email address.")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    if db.execute("SELECT * FROM users WHERE email=:email and password=:password" , {"email": email, "password": password}).rowcount == 1:
        alert_message = "Login succesful"
    else:
        alert_message = "Login failed"
    return render_template("index.html", logged_in=logged_in, alert_message=alert_message)

@app.route("/logout")
def logout():
    logged_in = False
    return redirect(url_for("index.html", logged_in=logged_in))

@app.route("/search", methods=["POST"])
def search():
    search_input = request.form.get("search_input")
    print(f"Searching for: {search_input}")
    if search_input is not None:
        search_results = db.execute("SELECT * FROM books WHERE UPPER(title) like :title or UPPER(author) like :author or UPPER(isbn) like :isbn", {"title": f"%{search_input.upper()}%", "author": f"%{search_input.upper()}%", "isbn": f"%{search_input.upper()}%"}).fetchall()
        results_count = len(search_results)
        if search_results == []:
            results_message = f"No books found for: {search_input}"
        else:
            results_message = f"Showing {results_count} search results for: {search_input}"
        return render_template("books.html", search_results=search_results, results_count=results_count, logged_in=logged_in, results_message=results_message)

@app.route("/books/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    if request.method == "POST":
        review_title = request.form.get("review_title")
        review = request.form.get("review")
        print(review_title)
        print(review)
        date = date.today()
        db.execute("INSERT INTO reviews(book_id, title, message, year) VALUES(:book_id, :title, :message, :date, :user_id)",
        {"book_id": book_id, "title": review_title, "message": review, "date": date, "user_id": user_id})
        db.commit()
    else:
        book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id": book_id}).fetchone()
        if book is None:
            return render_template("books.html", logged_in=logged_in)

        response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "L4JJxvbz5DQuqwHGe9grw", "isbns": book.isbn})
        response_data = response.json()
        reviews_count = response_data["books"][0]["reviews_count"]
        average_rating = response_data["books"][0]["average_rating"]
        #db.execute("UDATE books(SET average_rating=:average_rating, reviews_count=:reviews_count WHERE id=:book_id), {"book_id": book_id, "average_rating": average_rating, "reviews_count": reviews_count}")
        #db.commit()
        reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchall()
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
