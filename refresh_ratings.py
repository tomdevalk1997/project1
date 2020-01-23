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

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def refresh_ratings():
    print("Updating table")
    books = db.execute("SELECT * FROM books").fetchall()
    for book in books:
        response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "L4JJxvbz5DQuqwHGe9grw", "isbns": book.isbn})
        try:
            response_data = response.json()
            reviews_count = response_data["books"][0]["reviews_count"]
            average_rating = response_data["books"][0]["average_rating"]
            db.execute("UPDATE books SET average_rating=:average_rating, reviews_count=:reviews_count WHERE id=:book_id", {"average_rating": average_rating, "reviews_count": reviews_count, "book_id": book.id})
            print(f"Updated {book.id} with rating {average_rating} and review count {reviews_count}")
        except json.decoder.JSONDecodeError:
            db.execute("UPDATE books SET average_rating=:average_rating, reviews_count=:reviews_count WHERE id=:book_id", {"average_rating": 0, "reviews_count": 0, "book_id": book.id})
            print(f"Updated {book.id} with rating 0 and review count 0")
    db.commit()
    print("Table updated")

if __name__ == "__main__":
    refresh_ratings()
