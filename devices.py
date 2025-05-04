from flask import session, abort, render_template, request, redirect, url_for, flash, send_from_directory, current_app
import db
import os
from werkzeug.utils import secure_filename

from main_app import app
from constants import DEVICE_STATUS_MAP
from datetime import datetime


REPORT_FOLDER = "user_saved_reports"
ALLOWED_EXTENSIONS = "pdf"
MAX_FILE_SIZE = 10 * 1024 * 1024  #10MB
app.config["REPORT_FOLDER"] = REPORT_FOLDER


def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)


#Route for listing and sorting all devices
@app.route("/list_devices")
def devices():
    if "user_id" not in session:
        return redirect(url_for("login"))

    sort_by = request.args.get("sort_by", "device_id")  #Sort by device_id by default
    sort_order = request.args.get("sort_order", "asc")  #Ascending order as default

    #Validate user input
    if sort_by not in ["device_id", "type", "manufacturer", "status", "location"]:
        sort_by = "device_id"
    if sort_order not in ["asc", "desc"]:
        sort_order = "asc"

    sql = f"SELECT * FROM devices ORDER BY {sort_by} {sort_order}"
    devices = db.query(sql)

    devices = [dict(device) for device in devices]
    for device in devices:
        device["status"] = DEVICE_STATUS_MAP.get(device["status"], "Unknown status")

    return render_template("list_devices.html", devices=devices, sort_by=sort_by, sort_order=sort_order)


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
    check_csrf()

    type = request.form["type"].strip()
    manufacturer = request.form["manufacturer"].strip()
    model = request.form["model"].strip()
    manufacturer_serial = request.form["manufacturer_serial"].strip()
    location = request.form["location"].strip()
    status = request.form["status"]

    if not type:
        flash("Laitteen tyyppi on pakollinen")
        return redirect(url_for("create_device"))
    if not manufacturer:
        flash("Valmistaja on pakollinen")
        return redirect(url_for("create_device"))
    if not model:
        flash("Malli on pakollinen")
        return redirect(url_for("create_device"))
    if not manufacturer_serial:
        flash("Sarjanumero on pakollinen")
        return redirect(url_for("create_device"))
    if not location:
        flash("Sijainti on pakollinen")
        return redirect(url_for("create_device"))
    if not status.isdigit() or int(status) not in DEVICE_STATUS_MAP:
        flash("Valittu tila ei ole kelvollinen")
        return redirect(url_for("create_device"))

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
        type,
        manufacturer,
        model,
        manufacturer_serial,
        location,
        session["user_id"],
        int(status)
    ])

    return redirect(url_for("devices"))


#Route for displaying detailed device info
@app.route("/device/<int:device_id>")
def device_details(device_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

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

    files = []
    prefix = f"{device_id}_"
    for filename in os.listdir(app.config["REPORT_FOLDER"]):
        if filename.startswith(prefix):
            files.append(filename)

    return render_template("device_details.html", device=device, device_status_map=DEVICE_STATUS_MAP, files=files)


#Route for device information edit form
@app.route("/devices/<int:device_id>/edit")
def edit_device_form(device_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    sql = "SELECT * FROM devices WHERE device_id = ?"
    device = db.query(sql, [device_id])[0]

    return render_template("edit_device.html", device=device)


#Route for posting the device information editing form
@app.route("/devices/<int:device_id>/update", methods=["POST"])
def edit_device(device_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()

    type = request.form["type"].strip()
    manufacturer = request.form["manufacturer"].strip()
    model = request.form["model"].strip()
    manufacturer_serial = request.form["manufacturer_serial"].strip()
    location = request.form["location"].strip()

    if not type:
        flash("Laitteen tyyppi on pakollinen")
        return redirect(url_for("edit_device"))
    if not manufacturer:
        flash("Valmistaja on pakollinen")
        return redirect(url_for("edit_device"))
    if not model:
        flash("Malli on pakollinen")
        return redirect(url_for("edit_device"))
    if not manufacturer_serial:
        flash("Sarjanumero on pakollinen")
        return redirect(url_for("edit_device"))
    if not location:
        flash("Sijainti on pakollinen")
        return redirect(url_for("edit_device"))

    sql = """UPDATE devices SET 
             type = ?, 
             manufacturer = ?, 
             model = ?, 
             manufacturer_serial = ?,
             location = ? 
             WHERE device_id = ?
         """
    db.execute(sql, [type, manufacturer, model, manufacturer_serial, location, device_id])

    return redirect(url_for("device_details", device_id=device_id))


#Route for posting the device maintenance status update form
@app.route("/device/<int:device_id>/update_maintenance_status", methods=["POST"])
def update_maintenance_status(device_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()

    try:
        status = int(request.form["status"])
        if status not in DEVICE_STATUS_MAP:
            return "VIRHE: Virheellinen status", 400
    except (ValueError, KeyError):
        return "VIRHE: Status puuttuu tai ei ole kokonaisluku", 400

    next_maintenance = request.form.get("next_maintenance", "").strip()
    if next_maintenance:
        try:
            parsed_date = datetime.strptime(next_maintenance, "%Y-%m-%d")
            next_maintenance = parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            flash("Väärä päivämäärämuoto")
            return redirect(url_for("device_details", device_id=device_id))
    else:
        next_maintenance = None


    sql = "UPDATE devices SET status = ?, next_maintenance = ? WHERE device_id = ?"
    db.execute(sql, [status, next_maintenance, device_id])

    return redirect(url_for("device_details", device_id=device_id))


#Route for deleting devices
@app.route("/device/<int:device_id>/delete", methods=["POST"])
def delete_device(device_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()

    # Check if user has the device ownership
    sql = "SELECT owner_user_id FROM devices WHERE device_id = ?"
    result = db.query(sql, [device_id])

    if not result or result[0]["owner_user_id"] != session["user_id"]:
        flash("Vain vastuuhenkilö voi poistaa laitteen")
        return redirect(url_for("device_details", device_id=device_id))

    # Delete device if check was successful
    db.execute("DELETE FROM devices WHERE device_id = ?", [device_id])

    return redirect(url_for("devices"))


#Route for uploading reports for devices
@app.route("/device/<int:device_id>/upload", methods=["POST"])
def upload_device_file(device_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()

    if "file" not in request.files:
        flash("Ei tiedostoa valittuna", "error")
        return redirect(url_for("device_details", device_id=device_id))

    file = request.files["file"]
    if file.filename == "":
        flash("Tiedoston nimi puuttuu", "error")
        return redirect(url_for("device_details", device_id=device_id))

    if not file or "." not in file.filename or file.filename.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS:
        flash("Vain PDF-tiedostot sallittu", "error")
        return redirect(url_for("device_details", device_id=device_id))

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        flash("Vain alle 10MB kokoiset tiedostot sallittu", "error")
        return redirect(url_for("device_details", device_id=device_id))


    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["REPORT_FOLDER"], f"{device_id}_{filename}")
    file.save(filepath)
    flash("Tiedosto tallennettu", "success")
    return redirect(url_for("device_details", device_id=device_id))


#Route for showing uploaded reports
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["REPORT_FOLDER"], filename)


#Route for deleting uploaded reports
@app.route("/device/<int:device_id>/delete_file/<filename>", methods=["POST"])
def delete_device_file(device_id, filename):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()

    filepath = os.path.join(app.config["REPORT_FOLDER"], f"{device_id}_{filename}")
    try:
        os.remove(filepath)
        flash(f"Tiedosto {filename} poistettu", "success")
    except FileNotFoundError:
        flash("Tiedostoa ei löytynyt", "error")
    except Exception as e:
        flash(f"Tiedoston poisto epäonnistui: {str(e)}", "error")
    return redirect(url_for("device_details", device_id=device_id))
