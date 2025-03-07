from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure PostgreSQL database
db = SQL("postgresql://postgres:postgres@localhost:5432/autoservpro")


@app.route('/')
@app.route('/landing_page')
def landing_page():
    return render_template('landing_page.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/home')# Incomplete
def home():
    return render_template('home.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for owner
        rows = db.execute(
            "SELECT * FROM owner WHERE email = ?", request.form.get("email")
        )

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid email and/or password", 403)

        # Remember which user has logged in
        session["owner_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/home")

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

@app.route("/register", methods=["GET", "POST"])# Incomplete
def register():
    """Register user"""
    # Forget any user_id (just in case)
    session.clear()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # If any are blank
        if not email:
            return apology("must provide email", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confirmation:
            return apology("must provide confirmation password", 400)

        # Check if passwords match
        if password == confirmation:
            # Generate hash if true
            gen_pass = generate_password_hash(password)
        else:
            return apology("passwords don't match", 400)

        # Try executing query if username does not exist
        try:
            db.execute("INSERT INTO users (email, hash) VALUES (?, ?)", email, gen_pass)
            return redirect("/home")
        except ValueError:
            return apology("email already exists", 400)
    else:
        return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=True)