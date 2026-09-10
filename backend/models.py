from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    genre = db.Column(db.String(80), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(30), nullable=False)
    show_time = db.Column(db.String(30), nullable=False)
    bookings = db.relationship("Booking", backref="movie", lazy=True, cascade="all, delete-orphan")


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)
    number_of_tickets = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
