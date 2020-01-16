import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    csv_file = open("book.csv")
    reader = csv.reader(csv_file)
    for isbn, title, athor, year in reader:
        db.execut(e("INSERT INTO books(isbn, title, author, year) VALUE(:isbn, :title, :author, :year)", {"isbn":isbn, "title":title, "author":author, "year":year})
    db.commit()
