import os
import requests

from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError

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

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        user = User()
        user.first_name = request.form.get("first_name")
        user.last_name = request.form.get("last_name")
        user.email = request.form.get("email")
        user.username = request.form.get("username")
        user.password = request.form.get("password")

        try:
            # db.execute("INSERT INTO users (first_name, last_name, email, username, password) VALUES (:first_name, :last_name, :email, :username, :password)", {"first_name": first_name, "last_name": last_name, "email": email, "username": username, "password": password})
            db.add(user)
            db.commit()
            success_code = 1
            return render_template("success.html", message="You have been successfully signed up", success_code=success_code)
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
            return render_template("login.html", msg_invalid_username="Username not registered, please sign up")


        if(password == user.password):
            session["user_id"] = user["id"]
            return redirect(url_for("home", user_id=user.id))
        else:
            return render_template("login.html", msg_invalid_pw="Incorrect password, please try again")

@app.route("/logout")
def logout():
	session.clear()
	return redirect("/")