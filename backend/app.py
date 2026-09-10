from pathlib import Path
import os
import sys

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_cors import CORS

sys.path.insert(0, str(Path(__file__).resolve().parent))
from models import Booking, Movie, db


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "frontend" / "templates"),
    static_folder=str(BASE_DIR / "frontend" / "static"),
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "movie-booking-simple-secret")
database_url = os.environ.get("DATABASE_URL", f"sqlite:///{DATABASE_DIR / 'movie_booking.db'}")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
CORS(app, origins=os.environ.get("FRONTEND_URL", "*").split(","))


with app.app_context():
    db.create_all()
    if Movie.query.count() == 0:
        db.session.add_all(
            [
                Movie(title="Midnight in Mumbai", genre="Drama", language="Hindi", duration="2h 10m", show_time="6:30 PM"),
                Movie(title="The Last Orbit", genre="Sci-Fi", language="English", duration="2h 24m", show_time="8:45 PM"),
                Movie(title="Ocean of Dreams", genre="Adventure", language="English", duration="1h 58m", show_time="4:00 PM"),
            ]
        )
        db.session.commit()


def movie_data(movie):
    return {
        "id": movie.id,
        "title": movie.title,
        "genre": movie.genre,
        "language": movie.language,
        "duration": movie.duration,
        "show_time": movie.show_time,
    }


def booking_data(booking):
    return {
        "id": booking.id,
        "customer_name": booking.customer_name,
        "movie_id": booking.movie_id,
        "movie_title": booking.movie.title,
        "show_time": booking.movie.show_time,
        "number_of_tickets": booking.number_of_tickets,
        "total_amount": booking.total_amount,
    }


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/movies")
def api_movies():
    return jsonify([movie_data(movie) for movie in Movie.query.order_by(Movie.id.desc()).all()])


@app.post("/api/movies")
def api_add_movie():
    data = request.get_json() or {}
    fields = ("title", "genre", "language", "duration", "show_time")
    if any(not str(data.get(field, "")).strip() for field in fields):
        return jsonify({"error": "All movie fields are required."}), 400
    movie = Movie(**{field: str(data[field]).strip() for field in fields})
    db.session.add(movie)
    db.session.commit()
    return jsonify(movie_data(movie)), 201


@app.put("/api/movies/<int:movie_id>")
def api_edit_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    data = request.get_json() or {}
    fields = ("title", "genre", "language", "duration", "show_time")
    if any(not str(data.get(field, "")).strip() for field in fields):
        return jsonify({"error": "All movie fields are required."}), 400
    for field in fields:
        setattr(movie, field, str(data[field]).strip())
    db.session.commit()
    return jsonify(movie_data(movie))


@app.delete("/api/movies/<int:movie_id>")
def api_delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return jsonify({"status": "deleted"})


@app.get("/api/bookings")
def api_bookings():
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    return jsonify([booking_data(booking) for booking in bookings])


@app.post("/api/bookings")
def api_add_booking():
    data = request.get_json() or {}
    customer_name = str(data.get("customer_name", "")).strip()
    movie = Movie.query.get(data.get("movie_id"))
    tickets = data.get("number_of_tickets")
    if not customer_name or not movie or not isinstance(tickets, int) or not 1 <= tickets <= 10:
        return jsonify({"error": "Enter a name, movie, and 1 to 10 tickets."}), 400
    booking = Booking(customer_name=customer_name, movie_id=movie.id, number_of_tickets=tickets, total_amount=tickets * 150)
    db.session.add(booking)
    db.session.commit()
    return jsonify(booking_data(booking)), 201


@app.put("/api/bookings/<int:booking_id>")
def api_edit_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    data = request.get_json() or {}
    customer_name = str(data.get("customer_name", "")).strip()
    movie = Movie.query.get(data.get("movie_id"))
    tickets = data.get("number_of_tickets")
    if not customer_name or not movie or not isinstance(tickets, int) or not 1 <= tickets <= 10:
        return jsonify({"error": "Enter a name, movie, and 1 to 10 tickets."}), 400
    booking.customer_name = customer_name
    booking.movie_id = movie.id
    booking.number_of_tickets = tickets
    booking.total_amount = tickets * 150
    db.session.commit()
    return jsonify(booking_data(booking))


@app.delete("/api/bookings/<int:booking_id>")
def api_delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    return jsonify({"status": "deleted"})


@app.route("/")
def index():
    movies = Movie.query.order_by(Movie.id.desc()).limit(3).all()
    return render_template("index.html", movies=movies)


@app.route("/movies")
def movies():
    return render_template("movies.html", movies=Movie.query.order_by(Movie.id.desc()).all())


@app.route("/movies/add", methods=["GET", "POST"])
def add_movie():
    if request.method == "POST":
        movie = Movie(
            title=request.form["title"].strip(),
            genre=request.form["genre"].strip(),
            language=request.form["language"].strip(),
            duration=request.form["duration"].strip(),
            show_time=request.form["show_time"].strip(),
        )
        db.session.add(movie)
        db.session.commit()
        flash("Movie added successfully.", "success")
        return redirect(url_for("movies"))
    return render_template("add_movie.html")


@app.route("/movies/edit/<int:id>", methods=["GET", "POST"])
def edit_movie(id):
    movie = Movie.query.get_or_404(id)
    if request.method == "POST":
        movie.title = request.form["title"].strip()
        movie.genre = request.form["genre"].strip()
        movie.language = request.form["language"].strip()
        movie.duration = request.form["duration"].strip()
        movie.show_time = request.form["show_time"].strip()
        db.session.commit()
        flash("Movie updated successfully.", "success")
        return redirect(url_for("movies"))
    return render_template("edit_movie.html", movie=movie)


@app.route("/movies/delete/<int:id>")
def delete_movie(id):
    movie = Movie.query.get_or_404(id)
    db.session.delete(movie)
    db.session.commit()
    flash("Movie deleted.", "success")
    return redirect(url_for("movies"))


@app.route("/book", methods=["GET", "POST"])
def book():
    movies = Movie.query.order_by(Movie.title).all()
    booking = None
    if request.args.get("edit"):
        booking = Booking.query.get_or_404(request.args.get("edit", type=int))

    if request.method == "POST":
        movie_id = request.form.get("movie_id", type=int)
        tickets = request.form.get("number_of_tickets", type=int)
        customer_name = request.form["customer_name"].strip()
        movie = Movie.query.get_or_404(movie_id)

        if not customer_name or not tickets or tickets < 1:
            flash("Enter a name and at least one ticket.", "error")
            return render_template("book.html", movies=movies, booking=booking)

        booking_id = request.form.get("booking_id", type=int)
        if booking_id:
            booking = Booking.query.get_or_404(booking_id)
            booking.customer_name = customer_name
            booking.movie_id = movie.id
            booking.number_of_tickets = tickets
            booking.total_amount = tickets * 150
            message = "Booking updated successfully."
        else:
            booking = Booking(
                customer_name=customer_name,
                movie_id=movie.id,
                number_of_tickets=tickets,
                total_amount=tickets * 150,
            )
            db.session.add(booking)
            message = "Tickets booked successfully."

        db.session.commit()
        flash(message, "success")
        return redirect(url_for("bookings"))

    return render_template("book.html", movies=movies, booking=booking)


@app.route("/bookings")
def bookings():
    return render_template("bookings.html", bookings=Booking.query.order_by(Booking.id.desc()).all())


@app.route("/bookings/edit/<int:id>")
def edit_booking(id):
    Booking.query.get_or_404(id)
    return redirect(url_for("book", edit=id))


@app.route("/bookings/delete/<int:id>")
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    db.session.delete(booking)
    db.session.commit()
    flash("Booking deleted.", "success")
    return redirect(url_for("bookings"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
