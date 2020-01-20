import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("ec2-79-125-2-142.eu-west-1.compute.amazonaws.com:5432/dej617ep6sqm62"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    csv_file = open("books.csv")
    reader = csv.reader(csv_file)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books(isbn, title, author, year) VALUE(:isbn, :title, :author, :year)", {"isbn":isbn, "title":title, "author":author, "year":year})
        print(f"Added book with ISBN: {isbn}, title: {title}, author: {author} and year: {year}")
    db.commit()

if __name__ == "__main__":
    main()
