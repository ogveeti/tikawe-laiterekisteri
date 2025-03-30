from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

#Map device status codes to readable text
DEVICE_STATUS_MAP: dict[int, str] = {
    0: "Voimassa",
    1: "Umpeutunut",
    2: "Työn alla",
    3: "Vain tarvittaessa",
    4: "Ei seurannan piirissä",
    5: "Laite rikki",
    6: "Laite poistettu käytöstä"
}


#Route for the index page
@app.route("/")
def index():
    return render_template("index.html")


#Route for user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return "VIRHE: salasanat eivät ole samat"
        password_hash = generate_password_hash(password1)

        try:
            sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            db.execute(sql, [username, password_hash])
        except:
            return "VIRHE: käyttäjätunnus on jo varattu"

        return redirect(url_for("index"))

    return render_template("register.html")


#Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT user_id, password_hash FROM users WHERE username = ?"
        user = db.query(sql, [username])

        if not user or not check_password_hash(user[0]["password_hash"], password):
            return "VIRHE: väärä käyttäjätunnus tai salasana"

        session["user_id"] = user[0]["user_id"]
        session["username"] = username
        return redirect(url_for("devices"))

    return render_template("login.html")


#Route for user logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


#Route for listing all devices
@app.route("/list_devices")
def devices():
    if 'username' not in session:
        return redirect(url_for('login'))

    sql = "SELECT * FROM devices"
    devices = db.query(sql)

    devices = [dict(device) for device in devices]
    for device in devices:
        device["status"] = DEVICE_STATUS_MAP.get(device["status"], "Tuntematon status")

    return render_template("list_devices.html", devices=devices)


#Route for new device creation form
@app.route("/create_device_form", methods=["GET"])
def create_device_form():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("create_device.html", device_status_map=DEVICE_STATUS_MAP)


#Route for handling new device creation
@app.route("/create_device", methods=["POST"])
def create_device():
    if "user_id" not in session:
        return redirect(url_for("login"))

    sql = """INSERT INTO devices (
            type, 
            manufacturer, 
            model, 
            manufacturer_serial, 
            location, 
            owner_user_id, 
            status, 
            created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)"""

    db.execute(sql, [
        request.form["type"],
        request.form["manufacturer"],
        request.form["model"],
        request.form["manufacturer_serial"],
        request.form["location"],
        session["user_id"],
        request.form["status"]
    ])

    return redirect(url_for("devices"))


#Route for diplaying detailed device info
@app.route("/device/<int:device_id>")
def device_details(device_id):
    sql = """SELECT devices.*,
            users.username AS owner_name
            FROM devices JOIN users 
            ON devices.owner_user_id = users.user_id
            WHERE devices.device_id = ?"""
    result = db.query(sql, [device_id])

    if not result:
        return "VIRHE: Laitetta ei löytynyt", 404

    device = result[0]
    device = dict(device)
    device["status"] = DEVICE_STATUS_MAP.get(device["status"], "Tuntematon status")

    return render_template("device_details.html", device=device, device_status_map=DEVICE_STATUS_MAP)


#Route for device information edit form
@app.route("/devices/<int:device_id>/edit")
def edit_device_form(device_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    sql = "SELECT * FROM devices WHERE device_id = ?"
    device = db.query(sql, [device_id])[0]

    return render_template("edit_device.html", device=device)


#Route for posting the device information editing form
@app.route("/devices/<int:device_id>/update", methods=["POST"])
def edit_device(device_id):
    type = request.form["type"]
    manufacturer = request.form["manufacturer"]
    model = request.form["model"]
    manufacturer_serial = request.form["manufacturer_serial"]
    location = request.form["location"]
    status = request.form["status"]

    sql = """UPDATE devices SET 
             type = ?, 
             manufacturer = ?, 
             model = ?, 
             manufacturer_serial = ?,
             location = ?, 
             status = ? 
             WHERE device_id = ?
         """
    db.execute(sql, [type, manufacturer, model, manufacturer_serial, location, status, device_id])

    return redirect(url_for("device_details", device_id=device_id))


#Route for posting the device maintenance status update form
@app.route("/device/<int:device_id>/update_maintenance_status", methods=["POST"])
def update_maintenance_status(device_id):
    status = request.form["status"]
    next_maintenance = request.form["next_maintenance"] or None

    sql = "UPDATE devices SET status = ?, next_maintenance = ? WHERE device_id = ?"
    db.execute(sql, [status, next_maintenance, device_id])

    return redirect(url_for("device_details", device_id=device_id))


#Route for deleting devices
@app.route("/device/<int:device_id>/delete", methods=["POST"])
def delete_device(device_id):
    # Check if user has the device ownership
    sql = "SELECT owner_user_id FROM devices WHERE device_id = ?"
    result = db.query(sql, [device_id])

    if not result or result[0]["owner_user_id"] != session["user_id"]:
        return "VIRHE: Vain vastuuhenkilö voi poistaa laitteen", 403

    # Delete device if check was successful
    db.execute("DELETE FROM devices WHERE device_id = ?", [device_id])

    return redirect(url_for("devices"))
