from flask import Flask, render_template
import config

app = Flask(__name__)
app.secret_key = config.secret_key

from users import *
from devices import *


#Route for the index page
@app.route("/")
def index():
    return render_template("index.html")
