import os

from cs50 import SQL
import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///birthdays.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # TODO: Add the user's entry into the database
        bday = request.form["birthday"]
        name = request.form["name"]
        month, day = bday.split("/")
        conn = sqlite3.connect('birthdays.db')
        # conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO birthdays (name, month, day) VALUES ('{name}',{month},{day})")
        conn.commit()
        conn.close()

        return redirect("/")

    else:

        # TODO: Display the entries in the database on index.html
        conn = sqlite3.connect('birthdays.db')
        conn.row_factory = sqlite3.Row
        entries = conn.execute('SELECT * FROM birthdays').fetchall()
        conn.close()
        params = {"entries":entries}

        return render_template("index.html", **params)


