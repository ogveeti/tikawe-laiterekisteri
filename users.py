from flask import request, session, redirect, url_for, render_template, flash
from werkzeug.security import check_password_hash, generate_password_hash
from app_init import app
from constants import DEVICE_STATUS_MAP
import db
import secrets


#Route for user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if not username:
            flash("Käyttäjätunnus ei saa olla tyhjä")
            return redirect(url_for("register"))
        if not password1 or not password2:
            flash("Salasana ei saa olla tyhjä")
            return redirect(url_for("register"))
        if password1 != password2:
            flash("Salasanat eivät täsmää")
            return redirect(url_for("register"))
        password_hash = generate_password_hash(password1)

        try:
            sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            db.execute(sql, [username, password_hash])
        except:
            flash("Käyttäjätunnus on jo varattu")
            return redirect(url_for("register"))

        return redirect(url_for("index"))

    return render_template("register.html")


#Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            flash("Käyttäjätunnus ja salasana ovat pakollisia")
            return redirect(url_for("login"))

        user = db.query("SELECT user_id, password_hash FROM users WHERE username = ?", [username])

        if not user or not check_password_hash(user[0]["password_hash"], password):
            flash("Väärä käyttäjätunnus tai salasana")
            return redirect(url_for("login"))

        session["user_id"] = user[0]["user_id"]
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        db.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?", [user[0]["user_id"]])
        return redirect(url_for("devices"))

    return render_template("login.html")


#Route for user logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


#Route for listing all users
@app.route("/users")
def list_users():
    if "user_id" not in session:
        return redirect(url_for("login"))

    users = db.query("SELECT user_id, username FROM users")
    users = [dict(user) for user in users]

    counts = db.query("SELECT owner_user_id, COUNT(*) AS device_count FROM devices GROUP BY owner_user_id")
    device_counts = {row["owner_user_id"]: row["device_count"] for row in counts}

    for user in users:
        user["device_count"] = device_counts.get(user["user_id"], 0)

    return render_template("list_users.html", users=users, user_count=len(users))


#Route for showing individual user details
@app.route("/user/<int:user_id>")
def user_page(user_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_data = db.query("SELECT username, last_login FROM users WHERE user_id = ?", [user_id])
    if not user_data:
        return "VIRHE: Käyttäjää ei löytynyt", 404

    devices = db.query("SELECT * FROM devices WHERE owner_user_id = ?", [user_id])
    devices = [dict(device) for device in devices]
    for device in devices:
        device["status"] = DEVICE_STATUS_MAP.get(device["status"], "Tuntematon status")

    return render_template("user_page.html", user=dict(user_data[0]), devices=devices)
