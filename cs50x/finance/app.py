import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

import sqlite3

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
# sloppy... pk_4ed7b5ad3f3e42158ff42119a6a1a31b
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

def get_connection():
    conn = sqlite3.connect("finance.db")
    cur = conn.cursor()
    return conn, cur

def close_connection(conn):
    conn.commit()
    conn.close()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    sid = session["user_id"]
    conn, cur = get_connection()
    username, cash = cur.execute(f"SELECT username, cash from users WHERE id={sid};").fetchall()[0]
    stocks = cur.execute(f"SELECT symbol, sum(amount) from purchases WHERE user_id={sid} GROUP BY symbol;").fetchall()
    portfolio = [(symbol, amt, lookup(symbol)["price"]) for symbol, amt in stocks]
    pValue = sum(t[1]*t[2] for t in portfolio)+cash
    params = {
        "username":username,
        "stocks":portfolio,
        "cash": cash,
        "portfolio_value": pValue
    }
    close_connection(conn)
    return render_template("index.html", **params)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    elif request.method == "POST":
        symbol = request.form["symbol"]
        amt = request.form["shares"]
        price = request.form["price"]
        if not amt.isnumeric():
            return apology("amount not a number")
        if not price.isnumeric():
            return apology("price is not a number")
        price = int(price)
        if price <= 0:
            return apology("non-positive price")
        amt = int(amt)
        if amt <= 0:
            return apology("non-positive amount")
        total = price*amt
        conn, cur = get_connection()
        sid = session["user_id"]
        avCash = cur.execute(f"SELECT cash from users WHERE id={sid};").fetchall()
        avCash = int(avCash[0][0])
        if total > avCash:
            return apology("you don't have enough cash")
        remaining = avCash - total
        cur.execute(f"UPDATE users SET cash={remaining} WHERE id={sid}")
        cur.execute(f"INSERT INTO purchases (user_id, symbol, amount) VALUES ({sid},'{symbol}',{amt})")
        close_connection(conn)
        return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    conn, cur = get_connection()
    sid = session["user_id"]
    transactions = cur.execute(f"SELECT symbol, amount, timestamp from purchases where user_id={sid}").fetchall()
    params = {
        "purchases":transactions
    }
    close_connection(conn)
    return render_template("history.html", **params)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        return render_template("quote.html")
    elif request.method == "POST":
        symbol = request.form["symbol"]
        data = dict(lookup(symbol))
        t = sorted([tuple((k,v)) for k,v in data.items()])
        params = {
            "items":t
        }
        return render_template("quoted.html", **params)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        if not username:
            return apology("username is blank")
        pwd = request.form["password"]
        if not pwd:
            return apology("no password entered")
        confirm = request.form["confirmation"]
        if not confirm:
            return apology("password confirmation is blank")
        if confirm != pwd:
            return apology("passwords do not match")
        pwdHash = generate_password_hash(pwd)
        conn, cur = get_connection()
        cur.execute(f"INSERT INTO users (username, hash) VALUES('{username}', '{pwdHash}');")
        close_connection(conn)

        return redirect("/login")
    elif request.method == "GET":
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        return render_template("sell.html")
    elif request.method == "POST":
        conn, cur = get_connection()
        sid = session["user_id"]
        stocks = cur.execute(f"SELECT symbol, sum(amount) from purchases WHERE user_id={sid} GROUP BY symbol;").fetchall()
        symbol = request.form["symbol"]
        price = request.form["price"]
        amt = request.form["shares"]
        portfolio = {s:a for s,a in stocks}
        if symbol not in portfolio:
            return apology("you don't own that stock")
        elif int(amt) > portfolio[symbol]:
            return apology("amount greater than what you own")
        namt = -int(amt)
        cur.execute(f"INSERT INTO purchases (user_id, symbol, amount) VALUES ({sid}, '{symbol}', {namt})")
        newCASH = int(amt)*price
        cur.execute(f"UPDATE users SET cash=cash+{newCASH} WHERE id={sid}")
        close_connection(conn)
        return redirect("/")
