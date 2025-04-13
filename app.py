from flask import render_template
from app_init import app
import users
import devices


#Route for the index page
@app.route("/")
def index():
    return render_template("index.html")
