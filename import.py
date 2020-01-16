import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("postgres://iutmwfhcnvzjeh:723a5f85dd12d10d4f2c44a58f7781d856595212cca2d1573a176598f4cec44d@ec2-79-125-2-142.eu-west-1.compute.amazonaws.com:5432/dej617ep6sqm62"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    csv_file = open("book.csv")
    reader = csv.reader(csv_file)
    for isbn, title, athor, year in reader:
        db.execut(e("INSERT INTO books(isbn, title, author, year) VALUE(:isbn, :title, :author, :year)", {"isbn":isbn, "title":title, "author":author, "year":year})
    db.commit()
