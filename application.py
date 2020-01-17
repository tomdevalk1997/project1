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

@app.route("/books/<int:book_id>")
def book(book_id):
    #Lists details about a book

    # Make sure book exists
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if flight is None:
        return render_template("error.html", message="No such flight.")

    # Get all reviews
    #reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
    #return render_template("book.html", book=book, reviews=reviews)
    return render_template("book.html", book=book)
