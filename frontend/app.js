const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:5000"
    : "https://YOUR-RENDER-SERVICE.onrender.com";
const app = document.querySelector("#app");

const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
}[character]));

async function api(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
        headers: { "Content-Type": "application/json", ...(options.headers || {}) }, ...options,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "Something went wrong.");
    return data;
}

function layout(content) {
    app.innerHTML = content;
}

function movieCard(movie, actions = false, index = 0) {
    return `<article class="movie-card"><div class="poster poster-${(index % 3) + 1}"><span>${escapeHtml(movie.genre)}</span><strong>${escapeHtml(movie.title[0])}</strong></div>
        <div class="movie-info"><h3>${escapeHtml(movie.title)}</h3><p>${escapeHtml(movie.language)} · ${escapeHtml(movie.duration)}</p>
        <div class="movie-meta"><span>${escapeHtml(movie.show_time)}</span>${actions
            ? `<span class="actions"><a href="#/movie/edit/${movie.id}">Edit</a><a class="danger-link" href="#" data-delete-movie="${movie.id}">Delete</a></span>`
            : `<a href="#/book">Book →</a>`}</div></div></article>`;
}

async function home() {
    const movies = await api("/api/movies");
    layout(`<section class="hero"><div class="hero-content"><p class="eyebrow">YOUR NEXT GREAT STORY</p><h1>Book Your<br><em>Movie Tickets</em></h1><p class="hero-copy">Skip the queue, choose your perfect seats of the imagination, and make tonight a movie night.</p><a class="button primary" href="#/movies">Browse Movies <span>→</span></a></div><div class="hero-ticket"><span>NOW<br>SHOWING</span><strong>150</strong><small>per ticket</small></div></section><section class="section-head"><div><p class="eyebrow">ON THE BIG SCREEN</p><h2>Featured Movies</h2></div><a class="text-link" href="#/movies">View all movies →</a></section><section class="movie-grid">${movies.slice(0, 3).map((movie, index) => movieCard(movie, false, index)).join("")}</section>`);
}

async function moviesPage() {
    const movies = await api("/api/movies");
    layout(`<section class="page-header"><div><p class="eyebrow">THE LINEUP</p><h1>All Movies</h1><p>Manage the films currently playing at CineBook.</p></div><a class="button primary" href="#/movie/new">+ Add Movie</a></section><section class="movie-grid wide-grid">${movies.length ? movies.map((movie, index) => movieCard(movie, true, index)).join("") : empty("No movies yet", "Add your first movie to get started.", "#/movie/new")}</section>`);
    document.querySelectorAll("[data-delete-movie]").forEach((button) => button.onclick = async (event) => {
        event.preventDefault();
        if (confirm("Delete this movie?")) { await api(`/api/movies/${button.dataset.deleteMovie}`, { method: "DELETE" }); moviesPage(); }
    });
}

function empty(title, text, href) { return `<div class="empty-state"><h2>${title}</h2><p>${text}</p><a class="button primary" href="${href}">Get started</a></div>`; }
function movieForm(movie = {}) {
    return `<section class="form-page"><div class="form-heading"><p class="eyebrow">MOVIE MANAGEMENT</p><h1>${movie.id ? "Edit Movie" : "Add a Movie"}</h1><p>Keep the show details up to date.</p></div><form class="form-card" id="movie-form"><label>Movie Title<input name="title" value="${escapeHtml(movie.title)}" required></label><div class="form-row"><label>Genre<input name="genre" value="${escapeHtml(movie.genre)}" required></label><label>Language<input name="language" value="${escapeHtml(movie.language)}" required></label></div><div class="form-row"><label>Duration<input name="duration" value="${escapeHtml(movie.duration)}" placeholder="2h 10m" required></label><label>Show Time<input name="show_time" value="${escapeHtml(movie.show_time)}" placeholder="6:30 PM" required></label></div><div class="form-actions"><a class="button muted" href="#/movies">Cancel</a><button class="button primary" type="submit">Save Movie</button></div></form></section>`;
}

async function editMovie(id) {
    const movie = (await api("/api/movies")).find((item) => item.id === Number(id));
    if (!movie) return moviesPage();
    layout(movieForm(movie));
    document.querySelector("#movie-form").onsubmit = (event) => saveMovie(event, id);
}
async function saveMovie(event, id) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target));
    await api(id ? `/api/movies/${id}` : "/api/movies", { method: id ? "PUT" : "POST", body: JSON.stringify(data) });
    location.hash = "#/movies";
}

async function bookingForm(id) {
    const [movies, bookings] = await Promise.all([api("/api/movies"), api("/api/bookings")]);
    const booking = id ? bookings.find((item) => item.id === Number(id)) : null;
    layout(`<section class="form-page booking-page"><div class="form-heading"><p class="eyebrow">RESERVE YOUR SEATS</p><h1>${booking ? "Edit Booking" : "Book Your Tickets"}</h1><p>One ticket, one memory. Every ticket is ₹150.</p></div><form class="form-card" id="booking-form"><label>Customer Name<input name="customer_name" value="${escapeHtml(booking?.customer_name)}" required></label><label>Choose Movie<select name="movie_id" required><option value="">Select a movie</option>${movies.map((movie) => `<option value="${movie.id}" ${booking?.movie_id === movie.id ? "selected" : ""}>${escapeHtml(movie.title)} · ${escapeHtml(movie.show_time)}</option>`).join("")}</select></label><label>Number of Tickets<input type="number" name="number_of_tickets" value="${booking?.number_of_tickets || 1}" min="1" max="10" required></label><div class="price-box"><span>Total Amount</span><strong>₹150 <small>per ticket</small></strong></div><div class="form-actions"><a class="button muted" href="#/bookings">Cancel</a><button class="button primary" type="submit">${booking ? "Update Booking" : "Confirm Booking"}</button></div></form></section>`);
    document.querySelector("#booking-form").onsubmit = async (event) => {
        event.preventDefault();
        const data = Object.fromEntries(new FormData(event.target));
        data.movie_id = Number(data.movie_id); data.number_of_tickets = Number(data.number_of_tickets);
        await api(id ? `/api/bookings/${id}` : "/api/bookings", { method: id ? "PUT" : "POST", body: JSON.stringify(data) });
        location.hash = "#/bookings";
    };
}

async function bookingsPage() {
    const bookings = await api("/api/bookings");
    layout(`<section class="page-header"><div><p class="eyebrow">YOUR RESERVATIONS</p><h1>Bookings</h1><p>All ticket reservations in one place.</p></div><a class="button primary" href="#/book">+ New Booking</a></section><section class="booking-list">${bookings.length ? bookings.map((booking) => `<article class="booking-card"><div class="booking-number">#${String(booking.id).padStart(2, "0")}</div><div class="booking-main"><h3>${escapeHtml(booking.customer_name)}</h3><p>${escapeHtml(booking.movie_title)} · ${escapeHtml(booking.show_time)}</p></div><div class="booking-stat"><small>Tickets</small><strong>${booking.number_of_tickets}</strong></div><div class="booking-stat amount"><small>Total</small><strong>₹${booking.total_amount}</strong></div><div class="booking-actions"><a href="#/booking/edit/${booking.id}">Edit</a><a class="danger-link" href="#" data-delete-booking="${booking.id}">Delete</a></div></article>`).join("") : empty("No bookings yet", "Your confirmed tickets will appear here.", "#/book")}</section>`);
    document.querySelectorAll("[data-delete-booking]").forEach((button) => button.onclick = async (event) => { event.preventDefault(); if (confirm("Delete this booking?")) { await api(`/api/bookings/${button.dataset.deleteBooking}`, { method: "DELETE" }); bookingsPage(); } });
}

async function route() {
    try {
        const parts = location.hash.slice(2).split("/");
        if (!parts[0]) return home();
        if (parts[0] === "movies") return moviesPage();
        if (parts[0] === "movie") return parts[1] === "new" ? (layout(movieForm()), document.querySelector("#movie-form").onsubmit = saveMovie) : editMovie(parts[2]);
        if (parts[0] === "bookings") return bookingsPage();
        if (parts[0] === "book") return bookingForm();
        if (parts[0] === "booking" && parts[1] === "edit") return bookingForm(parts[2]);
        return home();
    } catch (error) { layout(`<div class="empty-state"><h2>Unable to connect</h2><p>${escapeHtml(error.message)}</p></div>`); }
}
window.addEventListener("hashchange", route);
route();
