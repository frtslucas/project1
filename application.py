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
    elif request.method == "POST":
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
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()

        if(password == user.password):
            session["user_id"] = user['id']
            return redirect(url_for('home', user_id=user.id))
        else:
            return render_template("login.html", message="Incorrect password, please try again")

@app.route("/home/<user_id>", methods=["GET"])
def home(user_id):
    user = db.execute("SELECT * FROM users WHERE id = :id", {"id": user_id}).fetchone()
    return render_template("home.html", user=user)

@app.route("/search", methods=["POST"])
def search():
    search_category = request.form.get("search_category")
    search_string = request.form.get("search_string")
    
    if(search_category == 'title'):
        book = db.execute("SELECT * FROM books WHERE title = :title", {"title": search_string}).fetchone()
    elif(search_category == 'author'):
        book = db.execute("SELECT * FROM books WHERE author = :author", {"author": search_string}).fetchone()
    elif(search_category == 'isbn'):
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": search_string}).fetchone()

    return render_template("book.html", book=book)