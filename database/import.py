import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://wqsqdaoijpennk:3906fa4aa6ee6edff819762e196802caabfa033eea806a9f0c4f88b69e8b4006@ec2-52-207-93-32.compute-1.amazonaws.com:5432/dejvlf4pubpuim")
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("../assets/books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added bookcle with ISBN: {isbn}.")
    db.commit()

if __name__ == "__main__":
    main()
