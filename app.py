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

# Configure MySQL database
db = SQL("mysql://sql8772963:sJH6JBf3a5@sql8.freesqldatabase.com/sql8772963")
# db = SQL("sqlite:///autoservpro.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/')
@app.route('/landing_page')
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

@login_required
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
            rows[0]["password"], request.form.get("password")
        ):
            return apology("invalid email and/or password", 403)

        # Remember which user has logged in
        session["owner_id"] = rows[0]["owner_id"]

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

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id (just in case)
    session.clear()

    if request.method == "POST":
        # Retrieve form data
        firstname = request.form.get("firstname")
        lastName = request.form.get("lastname")
        address = request.form.get("address")
        email = request.form.get("email")
        phoneNumber = request.form.get("phone")
        password = request.form.get("password")
        confirmation = request.form.get("confirm_password")
        car_vin_num = request.form.get("vin")
        make = request.form.get("make")
        licensePlate = request.form.get("license_plate")
        model = request.form.get("model")
        color = request.form.get("color")
        yearModel = request.form.get("year")

        # Validate inputs
        if not all([firstname, lastName, address, email, phoneNumber, password, confirmation, car_vin_num, make, licensePlate, model, color, yearModel]):
            return apology("All fields must be filled", 400)

        # Check if passwords match
        if password != confirmation:
            return apology("Passwords don't match", 400)
        
        if len(car_vin_num) != 13:
            return apology("VIN must be 13 characters", 400)
        
        # Generate hash for password
        gen_pass = generate_password_hash(password)

        # Try inserting user data into database
        try:
            owner_id = db.execute(
                """
                INSERT INTO owner (firstname, lastName, address, email, phoneNumber, password, user_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, 
                firstname, lastName, address, email, phoneNumber, gen_pass, "client"
            )
            
            # Insert car details associated with the user
            db.execute(
                """
                INSERT INTO car (owner_id, car_vin_num, make, licensePlate, model, color, yearModel)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, 
                owner_id, car_vin_num, make, licensePlate, model, color, yearModel
            )
            
            return redirect("/home")
        except ValueError:
            return apology("Email already exists", 400)
    
    else:
        return render_template("register.html")


# Display Functions
@login_required
@app.route("/home") # Displays owner information
def home():
    """Show owner information"""
    # Get owner's information from database
    owner_query = db.execute("select firstname, lastName, address, email, phoneNumber from owner where owner_id = ?", session["owner_id"])
    firstname = owner_query[0]["firstname"]
    lastname = owner_query[0]["lastName"]
    address = owner_query[0]["address"]
    email = owner_query[0]["email"]
    phone = owner_query[0]["phoneNumber"]
    return render_template("home.html", firstname=firstname, lastname=lastname, address=address, email=email, phone=phone)

@login_required
@app.route("/owner_cars") # Displays owner's cars
def owner_cars():
    """Show owner's cars"""
    # Get owner's cars from database
    owner_cars_query = db.execute("SELECT car_vin_num, make, licensePlate, model, color, yearModel FROM car WHERE owner_id = ?", session["owner_id"])
    return render_template("owner_cars.html", records=[{
        "vin": record["car_vin_num"],
        "make": record["make"],
        "license_plate": record["licensePlate"],
        "model": record["model"],
        "color": record["color"],
        "year": record["yearModel"]
    } for record in owner_cars_query])

@login_required
@app.route("/car_services") # Displays owner's services
def car_services():
    """Display services for all cars categorized by VIN"""
    cars = db.execute(
        "SELECT car_vin_num, price, description, datetime FROM service ORDER BY car_vin_num, datetime DESC"
    )
    
    # Organize services by VIN number
    car_services = {}
    for car in cars:
        vin = car["car_vin_num"]
        if vin not in car_services:
            car_services[vin] = []
        car_services[vin].append({
            "price": car["price"],
            "description": car["description"],
            "datetime": car["datetime"]
        })

    return render_template("car_services.html", car_services=car_services)


# Update Functions
@login_required
@app.route("/edit_profile", methods=["GET", "POST"]) # Updates Owner Information
def edit_profile():
    """Update owner information"""
    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastName = request.form.get("lastname")
        address = request.form.get("address")
        email = request.form.get("email")
        phoneNumber = request.form.get("phone")
        db.execute("UPDATE owner SET firstname = ?, lastName = ?, address = ?, email = ?, phoneNumber = ? WHERE owner_id = ?", firstname, lastName, address, email, phoneNumber, session["owner_id"])
        return redirect("/home")
    else:
        # Get owner's information from database
        owner_query = db.execute("select firstname, lastName, address, email, phoneNumber from owner where owner_id = ?", session["owner_id"])
        firstname = owner_query[0]["firstname"]
        lastname = owner_query[0]["lastName"]
        address = owner_query[0]["address"]
        email = owner_query[0]["email"]
        phone = owner_query[0]["phoneNumber"]
        return render_template("edit_profile.html", firstname=firstname, lastname=lastname, address=address, email=email, phone=phone)

@login_required
@app.route("/edit_car/<vin>", methods=["GET", "POST"]) # Edit Car Information
def edit_car(vin):
    """Update owner information"""
    if request.method == "POST":
        vin = request.form.get("vin")
        make = request.form.get("make")
        license_plate = request.form.get("license_plate")
        model = request.form.get("model")
        color = request.form.get("color")
        year = request.form.get("year")

        # Validate inputs
        if not all([vin, make, license_plate, model, color, year]):
            return apology("All fields must be filled", 400)
        
        # Validate VIN length
        if len(vin) != 13:
            return apology("VIN must be 13 characters", 400)
        
        # Try inserting car data into database
        try:
            db.execute(
                """
                UPDATE car SET make = ?, licensePlate = ?, model = ?, color = ?, yearModel = ? WHERE owner_id = ? AND car_vin_num = ?
                """, 
                make, license_plate, model, color, year, session["owner_id"], vin
            )
            return redirect("/owner_cars")
        except ValueError:
            return apology("Car not found", 400)
    else:
        car_query = db.execute("SELECT car_vin_num, make, licensePlate, model, color, yearModel FROM car WHERE owner_id = ? and car_vin_num = ?", session["owner_id"], vin)
        if len(car_query) != 1:
            return apology("Car not found", 404)
        car = car_query[0]
        return render_template("edit_car.html", vin=car["car_vin_num"], make=car["make"], license_plate=car["licensePlate"], model=car["model"], color=car["color"], year=car["yearModel"])

@login_required
@app.route("/change_password", methods=["GET", "POST"]) # Updates Owner Password
def change_password():
    """Change owner password"""
    if request.method == "POST":
        # Retrieve current password from database
        owner_query = db.execute("SELECT password FROM owner WHERE owner_id = ?", session["owner_id"])

        # Ensure query returned a result
        if not owner_query:
            return apology("User not found", 400)
        
        current_password = owner_query[0]["password"]

        # Verify current password input
        if check_password_hash(current_password, request.form.get("current_password")):
            # Validate new password and confirmation
            if request.form.get("new_password") != request.form.get("confirm_password"):
                return apology("Passwords don't match", 400)
            
            # Generate hash for new password
            new_pass = generate_password_hash(request.form.get("new_password"))
            
            # Update password in database
            db.execute("UPDATE owner SET password = ? WHERE owner_id = ?", new_pass, session["owner_id"])
            return redirect("/home")
        else:
            return apology("Current password is incorrect", 400)
    else:
        return render_template("change_password.html")


# Add Functions
@login_required
@app.route("/add_car", methods=["GET", "POST"])# Adds a Car
def add_car():
    if request.method == "POST":
        vin = request.form.get("vin")
        make = request.form.get("make")
        license_plate = request.form.get("license_plate")
        model = request.form.get("model")
        color = request.form.get("color")
        year = request.form.get("year")

        # Validate inputs
        if not all([vin, make, license_plate, model, color, year]):
            return apology("All fields must be filled", 400)
        
        # Validate VIN length
        if len(vin) != 13:
            return apology("VIN must be 13 characters", 400)
        
        # Try inserting car data into database
        try:
            db.execute(
                """
                INSERT INTO car (owner_id, car_vin_num, make, licensePlate, model, color, yearModel)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, 
                session["owner_id"], vin, make, license_plate, model, color, year
            )
            return redirect("/owner_cars")
        except ValueError:
            return apology("Car already exists", 400)
    else:
        return render_template("add_car.html")

@login_required
@app.route("/schedule", methods=["GET", "POST"]) # Adds a Service -> Incomplete!!!
def schedule():
    return render_template("schedule.html")

# Delete Functions
@login_required
@app.route("/delete_car/<vin>", methods=["POST"]) # Deletes a Car
def delete_car(vin):
    # Validate input
    if not vin:
        return apology("VIN must be provided", 400)
    
    # Try deleting car from database
    try:
        db.execute("DELETE FROM car WHERE owner_id = ? AND car_vin_num = ?", session["owner_id"], vin)
        return redirect("/owner_cars")
    except ValueError:
        return apology("Car not found", 400)


if __name__ == '__main__':
    app.run(debug=True)