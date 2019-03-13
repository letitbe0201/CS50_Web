import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


f = open("books.csv")
reader = csv.reader(f)
# print(reader)

db.execute("CREATE TABLE IF NOT EXISTS books ( id SERIAL PRIMARY KEY, isbn CHAR(16) NOT NULL, title VARCHAR(255) NOT NULL, author VARCHAR(255) NOT NULL, year CHAR(4) NOT NULL);")

for isbn, title, author, year in reader:
	db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year })
	print(f"added book {isbn} - {title} of {author} written in {year}")

db.commit()