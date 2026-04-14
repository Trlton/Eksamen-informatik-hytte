from flask import *
import webbrowser

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory("UI", "home.html")

@app.route("/<path:htmlFil>")
def static_files(htmlFil):
    return send_from_directory("UI", htmlFil)

webbrowser.open("http://localhost:5000")
app.run()
