import os

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_isbn = db.Column(db.Integer, db.ForeignKey('books.isbn'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.String, nullable=False)