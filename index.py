from flask import Flask, request, render_template
from lib.database import create_tables, get_shortened_url, get_decorations
from os import path
import sqlite3

template_dir = path.abspath('./templates')

app = Flask(__name__, template_folder=template_dir)


def get_connection():
    return sqlite3.connect("urls.db")


@app.route("/", methods=["GET"])
def home():
    return render_template("form.html")


@app.route("/", methods=["POST"])
def post_url():
    payload = request.get_json()
    url = payload.get("url")
    image = payload.get("image")
    title = payload.get("title")
    description = payload.get("description")
    name = payload.get("name")
    if url is None:
        return {"success": False, "error": "Missing URL"}
    shortened_url = get_shortened_url(
        get_connection(), url, image, title, description, name)
    return {"success": True, "url": shortened_url}


@app.route("/<shortened>", methods=["GET"])
def get_url(shortened):
    results = get_decorations(get_connection(), shortened)
    if results is None:
        return render_template("nope.html")
    url, image, title, description, name = results
    return render_template("index.html", url=url, title=title, description=description, name=name, image=image)


db = sqlite3.connect("urls.db")

if __name__ == "__main__":
    create_tables(get_connection())
    app.run()
