import os
import requests

from flask import Flask, session, flash, jsonify, redirect, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":

        search = request.form.get("search")
        # Searching the related data from the table books
        results = db.execute("SELECT * FROM books WHERE isbn LIKE :s OR title LIKE :s OR author LIKE :s",
        					 {"s": '%'+search+'%'}).fetchall()

        # Flash a message in response to the searching result
        if not search:
            flash('Please enter the ISBN, title or author!')
            return redirect("/")
        elif not results:
   	        # nothing found
            flash('No result!')
            return redirect("/")
        # Else return a result page
        else:
            return render_template("result.html", results=results, search=search)
    else:
        return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
        				 {"username": request.form.get("username")}).fetchall()

        # Ensure username exists and password is correct (by query database for username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# route for registeration
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username!", 400)
        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("Must provide password!", 400)
        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("Retype the password for confirmation!", 400)
        # Ensure the password matches the confirmation
        elif not (request.form.get("password") == request.form.get("confirmation")):
            return apology("Passwords don't match!", 400)

        # insert the info of user into the database
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :password)",
                    {"username": request.form.get("username"),
                     "password": generate_password_hash(request.form.get("password"))})
        # commit the insert (actually insert the data)
        db.commit()

        # Query database for username again to remember
        rows = db.execute("SELECT * FROM users WHERE username = :username",
        				 {"username": request.form.get("username")}).fetchone()
        # Remember which user has logged in
        session["user_id"] = rows["id"]

        # flashing the message on route /
        flash('REGISTERED!')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    # ensure the username length is at least one
    if not username:
        return jsonify(False)

    # Query database for username. If the len(rows)!=0, which means the username has been registered, then return false
    if db.execute("SELECT * FROM users WHERE username = :username",
    			 {"username": username}).rowcount != 0:
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/book/<string:isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):
    if request.method == "POST":

        # Query database for book info.
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
        				 {"isbn": isbn}).fetchone()

        # Get the info of the book from Goodreads
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
        					params={"key": "ep0w1uEv7e7r3gJlXnkA", "isbns": isbn}).json()

        # Ensure the user has rated the book
        if not request.form.get("rating"):
        	return apology("Must provide rating of the book!", 400)

        # Query database for the reviews of this book
        reviews = db.execute("SELECT * FROM reviews, users WHERE bookid = :book AND reviews.userid = users.id",
        					{"book": book["id"]}).fetchall()

        for review in reviews:
        	# Ensure the user doesn't submit multiple reviews for the same book
        	if review["userid"] == session["user_id"] and review["bookid"] == book["id"]:
        		# Return apology if a review has found
        		return apology("You have already rated this book!", 400)

        # Insert the user's comment to the database
        db.execute("INSERT INTO reviews (userid, bookid, rating, review) VALUES (:userid, :bookid, :rating, :review)",
        			{"userid": session["user_id"],"bookid": book["id"],"rating": request.form.get("rating"),
        			 "review": request.form.get("review")})
        db.commit()

        # Setup mycomment using in the html page
        mycomment = {'exist': 1, 'rating': request.form.get("rating"),
        			 'review': request.form.get("review"),
        			 'datetime': db.execute("SELECT datetime From reviews WHERE userid=:userid AND bookid=:bookid",
        			 						{"userid": session["user_id"], "bookid": book["id"]}).fetchone()["datetime"]}

        return render_template("book.html", book=book, res=res, reviews=reviews,
        						userid=session["user_id"], mycomment=mycomment)

    else:
        # Query database for book info.
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
        				 {"isbn": isbn}).fetchone()

        # Get the info of the book from Goodreads
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
        					params={"key": "ep0w1uEv7e7r3gJlXnkA", "isbns": isbn}).json()

        # Query database for the reviews of this book
        reviews = db.execute("SELECT * FROM reviews, users WHERE bookid = :book AND reviews.userid = users.id",
        					{"book": book["id"]}).fetchall()

        # Check whether the user has left a comment
        mycomment = {'exist': 0}
        for review in reviews:
        	if review["userid"] == session["user_id"] and review["bookid"] == book["id"]:
        		mycomment = {'exist': 1, 'rating': review["rating"],
        					 'review': review["review"], 'datetime': review["datetime"]}

        return render_template("book.html", book=book, res=res, reviews=reviews,
        						userid=session["user_id"], mycomment=mycomment)


@app.route("/api/<string:isbn>")
@login_required
def api(isbn):

    # Query database for book info.
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
    				 {"isbn": isbn}).fetchone()
    if not book:
    	return apology("Not found!", 404)

    # Get the info of the book from Goodreads
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
    					params={"key": "ep0w1uEv7e7r3gJlXnkA", "isbns": isbn}).json()

    # api for a given isbn
    api = {
    "title": book["title"],
    "author": book["author"],
    "year": book["year"],
    "isbn": book["isbn"],
    "review_count": res["books"][0]["work_ratings_count"],
    "average_score": res["books"][0]["average_rating"]
    }

    return jsonify(api)