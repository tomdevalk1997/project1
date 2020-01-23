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
import datetime

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def update_list():
    books = db.execute("SELECT * FROM books ORDER BY average_rating DESC LIMIT 10").fetchall()
    return books

@app.route("/")
def index():
    top10 = update_list()
    if session.get("logged_in") is None:
        session["logged_in"] = False
    return render_template("index.html", logged_in=session["logged_in"], alert_message="", top10=top10)

@app.route("/books", methods=["GET", "POST"])
def books():
    top10 = update_list()
    if request.method == "GET":
        return render_template("books.html", results_count=0, logged_in=session["logged_in"], top10=top10)
    else:
        search_results = db.execute("SELECT * FROM books WHERE title like '%input%' or author like '%input%' or isbn like '%input%'").fetchall()
        if search_results is None:
            print("No books found")
            return render_template("books.html", results_count=0, logged_in=session["logged_in"])
        return render_template("books.html", search_results=search_results, results_count=1, logged_in=session["logged_in"], top10=top10)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")

        if db.execute("SELECT * FROM users WHERE email=:email", {"email": email}).rowcount == 0:
            if password == password_confirmation:
                db.execute("INSERT INTO users(name, email, password) VALUES(:name, :email, :password)",
                    {"name": name, "email": email, "password": password})
                db.commit()
                alert_message = "Registration succesful"
                return render_template("index.html", logged_in=session["logged_in"], alert_message=alert_message)
            else:
                alert_message = "Passwords need to be the same to register."
                return render_template("register.html", logged_in=session["logged_in"], alert_message=alert_message)
        else:
            alert_message = "Email address is already present in the database. Log in or register a different email address."
            return render_template("register.html", logged_in=session["logged_in"], alert_message=alert_message)

@app.route("/login", methods=["POST"])
def login():
    top10 = update_list()
    email = request.form.get("email")
    password = request.form.get("password")
    login_user = db.execute("SELECT * FROM users WHERE email=:email and password=:password" , {"email": email, "password": password}).fetchone()
    if login_user is not None:
        alert_message = "Login succesful"
        session["user_id"] = login_user.id
        session["logged_in"] = True
    else:
        alert_message = "Login failed"
    return render_template("index.html", logged_in=session["logged_in"], alert_message=alert_message)

@app.route("/logout")
def logout():
    top10 = update_list()
    alert_message = "Logout succesful"
    session["logged_in"] = False
    return render_template("index.html", logged_in=session["logged_in"], alert_message=alert_message)

@app.route("/search", methods=["POST"])
def search():
    top10 = update_list()
    if session["logged_in"] == True:
        search_input = request.form.get("search_input")
        if search_input is not None:
            top10 = update_list()
            search_results = db.execute("SELECT * FROM books WHERE UPPER(title) like :title or UPPER(author) like :author or UPPER(isbn) like :isbn", {"title": f"%{search_input.upper()}%", "author": f"%{search_input.upper()}%", "isbn": f"%{search_input.upper()}%"}).fetchall()
            results_count = len(search_results)
            if search_results == []:
                results_message = f"No books found for: {search_input}"
            else:
                results_message = f"Showing {results_count} search results for: {search_input}"
            return render_template("books.html", search_results=search_results, results_count=results_count, logged_in=session["logged_in"], results_message=results_message, top10=top10)
    else:
        alert_message = "Please log in or register to search this website."
        return render_template("books.html", logged_in=session["logged_in"], results_count=0, alert_message=alert_message, top10=top10)

@app.route("/books/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    alert_message = ""
    top10 = update_list()
    if session["logged_in"] == True:
        if db.execute("SELECT * FROM reviews WHERE user_id=:user_id ", {"user_id": session["user_id"]}).rowcount > 0:
            if request.method == "POST":
                review_title = request.form.get("review_title")
                review = request.form.get("review")
                date_review = datetime.date.today()
                rating = request.form.get("inlineRadioOptions")
                print(rating)
                db.execute("INSERT INTO reviews(book_id, title, message, date, user_id, rating) VALUES(:book_id, :title, :message, :date, :user_id, :rating)",
                {"book_id": book_id, "title": review_title, "message": review, "date": date_review, "user_id": session["user_id"], "rating": rating})
                db.commit()
                alert_message = "Review posted succesfully"

            book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id": book_id}).fetchone()
            if book is None:
                return render_template("books.html", logged_in=session["logged_in"], )

            response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "L4JJxvbz5DQuqwHGe9grw", "isbns": book.isbn})
            try:
                response_data = response.json()
                reviews_count = response_data["books"][0]["reviews_count"]
                average_rating = response_data["books"][0]["average_rating"]
            except json.decoder.JSONDecodeError:
                reviews_count = 0
                average_rating = 0
            db.execute("UPDATE books SET average_rating=:average_rating, reviews_count=:reviews_count WHERE id=:book_id", {"average_rating": average_rating, "reviews_count": reviews_count, "book_id": book.id})
            db.commit()
            reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchall()
            return render_template("book.html", book=book, reviews_count=reviews_count, average_rating=average_rating, reviews=reviews, logged_in=session["logged_in"], alert_message=alert_message, top10=top10)
        else:
            alert_message = "You are unable to post multiple reviews for a single book."
            return render_template("books.html", logged_in=session["logged_in"], results_count=0, alert_message=alert_message, top10=top10)
    else:
        alert_message = "Please log in or register to view books and reviews."
        return render_template("books.html", logged_in=session["logged_in"], results_count=0, alert_message=alert_message, top10=top10)

@app.route("/api/books/<int:isbn>")
def book_api(book_id):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error": "unknown isbn"}), 404
    return jsonify({
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
        "year": book.year
    })
