import os

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not ("postgres://wqsqdaoijpennk:3906fa4aa6ee6edff819762e196802caabfa033eea806a9f0c4f88b69e8b4006@ec2-52-207-93-32.compute-1.amazonaws.com:5432/dejvlf4pubpuim"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://wqsqdaoijpennk:3906fa4aa6ee6edff819762e196802caabfa033eea806a9f0c4f88b69e8b4006@ec2-52-207-93-32.compute-1.amazonaws.com:5432/dejvlf4pubpuim")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return "Project 1: TODO"
