from flask import request, session, redirect, url_for, render_template, flash
from app_init import app
from constants import DEVICE_STATUS_MAP
from datetime import datetime
import db


#Route for listing and sorting all devices
@app.route("/list_devices")
def devices():
    if "username" not in session:
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
    if "username" not in session:
        return redirect(url_for("login"))

    sql = "SELECT * FROM devices WHERE device_id = ?"
    device = db.query(sql, [device_id])[0]

    return render_template("edit_device.html", device=device)


#Route for posting the device information editing form
@app.route("/devices/<int:device_id>/update", methods=["POST"])
def edit_device(device_id):
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
    # Check if user has the device ownership
    sql = "SELECT owner_user_id FROM devices WHERE device_id = ?"
    result = db.query(sql, [device_id])

    if not result or result[0]["owner_user_id"] != session["user_id"]:
        flash("Vain vastuuhenkilö voi poistaa laitteen")
        return redirect(url_for("device_details", device_id=device_id))

    # Delete device if check was successful
    db.execute("DELETE FROM devices WHERE device_id = ?", [device_id])

    return redirect(url_for("devices"))
