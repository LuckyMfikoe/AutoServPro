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

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/')
def landing_page():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


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

@app.route("/home") # Displays owner information
@login_required
def home():
    """Show owner information"""
     # Get owner's information from database
    owner_query = db.execute("select firstname, lastname, address, email, phone from owner where id = ?", session["owner_id"])
    firstname = owner_query[0]
    lastname = owner_query[1]
    address = owner_query[2]
    email = owner_query[3]
    phone = owner_query[4]
    return render_template("home.html", firstname=firstname, lastname=lastname, address=address, email=email, phone=phone)

@login_required
@app.route("/owner_cars") # Displays owner's cars -> Incomplete
def owner_cars():
    return render_template("owner_cars.html")


# Update Functions
@login_required
@app.route("/update_profile", methods=["GET", "POST"]) # Updates Owner Information
def update_profile():
    """Update owner information"""
    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        address = request.form.get("address")
        email = request.form.get("email")
        phone = request.form.get("phone")
        db.execute("UPDATE owner SET firstname = ?, lastname = ?, address = ?, email = ?, phone = ? WHERE id = ?", firstname, lastname, address, email, phone, session["owner_id"])
        return redirect("/home")
    else:
        return render_template("update_profile.html")

@login_required
@app.route("/update_car", methods=["GET", "POST"]) # Updates Car Information -> Incomplete
def update_car():
    """Update owner information"""
    if request.method == "POST":
        #firstname = request.form.get("firstname")
        #lastname = request.form.get("lastname")
        #address = request.form.get("address")
        #email = request.form.get("email")
        #phone = request.form.get("phone")
        #db.execute("UPDATE owner SET firstname = ?, lastname = ?, address = ?, email = ?, phone = ? WHERE id = ?", firstname, lastname, address, email, phone, session["owner_id"])
        return redirect("/home")
    else:
        return render_template("update_car.html")

if __name__ == '__main__':
    app.run(debug=True)