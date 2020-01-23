import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    csv_file = open("books.csv")
    reader = csv.reader(csv_file)
    for isbn, title, author, year in reader:
        # ISBN, title, author and year are added to the database for every book in books.csv
        db.execute("INSERT INTO books(isbn, title, author, year) VALUES(:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book with ISBN: {isbn}, title: {title}, author: {author} and year: {year}")
    db.commit()

if __name__ == "__main__":
    main()
