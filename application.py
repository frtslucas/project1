import os
import requests

from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError
from models import *

app = Flask(__name__)

# Check for environment variable
if not ("postgres://wqsqdaoijpennk:3906fa4aa6ee6edff819762e196802caabfa033eea806a9f0c4f88b69e8b4006@ec2-52-207-93-32.compute-1.amazonaws.com:5432/dejvlf4pubpuim"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = 'any secret string'
Session(app)

# Set up database
engine = create_engine("postgres://wqsqdaoijpennk:3906fa4aa6ee6edff819762e196802caabfa033eea806a9f0c4f88b69e8b4006@ec2-52-207-93-32.compute-1.amazonaws.com:5432/dejvlf4pubpuim")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        
        try:
            db.execute("INSERT INTO users (first_name, last_name, email, username, password) VALUES (:first_name, :last_name, :email, :username, :password)", {"first_name": first_name, "last_name": last_name, "email": email, "username": username, "password": password})
            db.commit()
            return render_template("success.html", message="You have been successfully signed up")
        except IntegrityError:
            return render_template("register.html", message="The username or email is already being used")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()

        if(user is None):
            return render_template("login.html", msg_invalid_username="Incorrect username, please try again")


        if(password == user.password):
            session["user_id"] = user["id"]
            return redirect(url_for("home", user_id=user.id))
        else:
            return render_template("login.html", msg_invalid_pw="Incorrect password, please try again")

@app.route("/logout")
def logout():
	session.clear()
	return redirect("/")
        
@app.route("/home/<int:user_id>")
def home(user_id):
    user = db.execute("SELECT * FROM users WHERE id = :id", {"id": user_id}).fetchone()
    return render_template("home.html", user=user)

@app.route("/home/")
def home_redirect():
    if (session.get('user_id') == True):
        user_id = session["user_id"]
        return redirect(url_for('home', user_id=user_id))
    else:
        return redirect(url_for('login'))

@app.route("/search/", methods=["GET"])
def search():
    args = request.args
    txtsearch = args["txtsearch"]
    category = args["category"]

    if(category == "title"):
       results = db.execute("SELECT * FROM books WHERE title ILIKE '%" + txtsearch + "%' ORDER BY year").fetchall()
    elif(category == "author"):
       results = db.execute("SELECT * FROM books WHERE author ILIKE '%" + txtsearch + "%' ORDER BY year").fetchall()
    elif(category == "year"):
       results = db.execute("SELECT * FROM books WHERE year ILIKE '%" + txtsearch + "%' ORDER BY year").fetchall()
    else:
        results = db.execute("SELECT * FROM books WHERE isbn ILIKE '%" + txtsearch + "%' ORDER BY year").fetchall()

    return render_template("search_results.html", results=results)

@app.route("/book/<string:book_isbn>", methods=["GET"])
def book(book_isbn):

    if (session.get('user_id') is None):
        return redirect(url_for('login'))

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    reviews = db.execute("SELECT r.id, r.rating, r.review_text, u.first_name, u.last_name FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.book_isbn = :book_isbn", {"book_isbn": book_isbn})

    res_goodreads = requests.get("https://www.goodreads.com/book/review_counts.json",
                    params={"key": "sKRIbzWWp8qizliHj7TsJg", "isbns": book_isbn})
    if res_goodreads.status_code != 200:
        raise Exception("ERROR: API request unsuccessfull")
    goodreads = res_goodreads.json()

    return render_template("book.html", book=book, reviews=reviews, goodreads=goodreads)

@app.route("/review/<string:book_isbn>", methods=["POST"])
def review(book_isbn):
    review = Review()
    review.user_id = session["user_id"]
    review.book_isbn = book_isbn
    review.rating = request.form.get("rating")
    review.review_text = request.form.get("review_text")

    if(db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_isbn = :book_isbn", {"user_id": review.user_id, "book_isbn": book_isbn}).rowcount == 0):
        db.add(review)
        db.commit()
    else:
        return render_template("error.html", message="You have already submitted a review to this book")
    return redirect(url_for('book', book_isbn=book_isbn))