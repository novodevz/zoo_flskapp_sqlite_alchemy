import os
import secrets

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Generate a random string for SECRET_KEY
app.config["SECRET_KEY"] = secrets.token_hex(16)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///zoo.db"
# Configure the upload folder
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.email}', '{self.password}')"


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Relationship with User
    user_email = db.Column(
        db.String(255), db.ForeignKey("user.email"), unique=True, nullable=False
    )
    user_info = db.relationship(
        "User", backref=db.backref("admin", uselist=False), lazy=True
    )

    def __repr__(self):
        return f"Admin('{self.id}', '{self.user_email}')"


def default_image_url():
    return url_for("static", filename="images/zoo.jpg")


class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)
    species = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(10), nullable=True)
    img = db.Column(
        db.String(255),
        nullable=True,
        default=default_image_url,
    )

    def __repr__(self):
        return f"Animal('{self.id}', '{self.name}', '{self.species}', '{self.description}')"


@app.route("/")
def index():
    return render_template("index.html")


from flask import session


@app.route("/signup", methods=["GET", "POST"])
def signup():
    # Check if the user is already logged in
    if session.get("is_loggedin"):
        flash("You are already logged in. Logout to create a new account.", "info")
        return redirect(url_for("zoo"))  # Redirect to the home page or any other page

    if request.method == "POST":
        email = request.form.get("email")
        # Check if the user already exists in the User table
        existing_user = User.query.filter_by(email=email).first()

        if not existing_user:
            # For simplicity, assuming password is valid and securely hashed in a real-world scenario
            password = request.form.get("password")
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash(f"Signup successful! Welcome, {new_user.email}", "success")
            return render_template("login.html")
            # return redirect(url_for("login"))
        else:
            flash("User with this email already exists. Please login.", "warning")
            return render_template("login.html")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        # Check if the user exists in the User table
        user = User.query.filter_by(email=email).first()

        if user:
            # Check login credentials (for simplicity, assume correct password for now)
            # In a real-world scenario, you would hash and compare passwords securely
            password = request.form.get("password")
            if user.password == password:
                session["is_loggedin"] = True
                flash(f"Login successful! Welcome, {user.email}", "success")
                # Add logic for user roles (admin, regular user) here

                if user.admin:
                    session["admin_user"] = True

                else:
                    session["admin_user"] = False

                return redirect(url_for("zoo"))
            else:
                flash("Incorrect password. Please try again.", "danger")
        else:
            flash("User does not exist. Please sign up first.", "warning")
            return render_template("signup.html")

    return render_template("login.html")


@app.route("/zoo")
def zoo():
    # Check if the user is logged in
    if not session.get("is_loggedin"):
        flash("You must be logged in to view our zoo.", "info")
        return redirect(url_for("index"))
    animals = Animal.query.all()
    return render_template("zoo.html", animals=animals)


from werkzeug.utils import secure_filename

# Define the allowed extensions for image files
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}


# Function to check if the file extension is allowed
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


import time

from werkzeug.utils import secure_filename


def default_image_url():
    return url_for("static", filename="images/zoo.jpg")


@app.route("/add", methods=["GET", "POST"])
def add():
    if not session.get("is_loggedin"):
        flash("You must be logged in as admin to add animals.", "danger")
        return redirect(url_for("login"))

    if not session.get("admin_user"):
        flash("Only admins can add animals.", "danger")
        return redirect(url_for("zoo"))

    if request.method == "POST":
        name = request.form.get("name")
        species = request.form.get("species")
        description = request.form.get("description")

        if "image" in request.files:
            image = request.files["image"]

            if image.filename != "" and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                timestamp = int(time.time())
                unique_filename = f"{timestamp}_{filename}"
                relative_path = os.path.join("uploads", unique_filename)

                # Ensure the "uploads" directory exists, and create it if not
                uploads_dir = os.path.join(app.root_path, "static", "uploads")
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)

                # Construct the absolute path to save the image
                absolute_path = os.path.join(uploads_dir, unique_filename)

                image.save(absolute_path)

                new_animal = Animal(
                    name=name,
                    species=species,
                    description=description,
                    img=relative_path,
                )
            else:
                new_animal = Animal(name=name, species=species, description=description)
        else:
            new_animal = Animal(name=name, species=species, description=description)

        try:
            db.session.add(new_animal)
            db.session.commit()
            flash(f"Animal '{new_animal.name}' added successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding animal: {str(e)}", "danger")

        return redirect(url_for("zoo"))

    return render_template("add.html")


@app.route("/update/<int:animal_id>", methods=["GET", "POST"])
def update(animal_id):
    # Check if the user is logged in
    if not session.get("is_loggedin"):
        flash("You must be logged in as admin to update animal information.", "danger")
        return redirect(url_for("login"))

    # Check if the logged-in user is an admin
    if not session.get("admin_user"):
        flash("Only admins can update animal information.", "danger")
        return redirect(url_for("zoo"))

    # Get the animal by ID or return a 404 error if not found
    animal = Animal.query.get(animal_id)
    if not animal:
        # flash(f"Animal with ID {animal_id} not found.", "danger")
        flash(f"Zoo is empty, add new animal", "info")
        return redirect(url_for("add"))

    if request.method == "POST":
        # Update animal information
        animal.name = request.form.get("name")
        animal.species = request.form.get("species")
        animal.description = request.form.get("description")

        db.session.commit()

        flash(f"Animal '{animal.name}' information updated successfully!", "success")
        return redirect(url_for("update", animal_id=animal.id))

    # On GET request, render the update form above the list of animals
    animals = Animal.query.all()
    return render_template(
        "update.html", animal=animal, animals=animals, animalId=animal_id
    )


import os

from flask import request


@app.route("/delete/<int:animal_id>", methods=["GET", "DELETE"])
def delete(animal_id):
    # Check if the user is logged in
    if not session.get("is_loggedin"):
        flash("You must be logged in as an admin to delete animals.", "danger")
        return redirect(url_for("login"))

    # Check if the logged-in user is an admin
    if not session.get("admin_user"):
        flash("Only admins can delete animals.", "danger")
        return redirect(url_for("zoo"))

    # If it's a GET request, render the delete page
    if request.method == "GET":
        # Get all animals for display
        animals = Animal.query.all()
        return render_template("delete.html", animals=animals)

    # If it's a DELETE request, handle the deletion
    animal = Animal.query.get_or_404(animal_id)

    # Get the image path and remove the file
    if animal.img:
        image_path = os.path.join("static", "uploads", os.path.basename(animal.img))
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(animal)
    db.session.commit()

    flash(f"Animal '{animal.name}' deleted successfully!", "success")

    # Return a response, e.g., a JSON response
    return jsonify({"message": f"Animal '{animal.name}' deleted successfully!"})


@app.route("/logout")
def logout():
    # Check if the user is already logged out
    if not session.get("is_loggedin"):
        flash("You are already logged out.", "info")
        return redirect(url_for("login"))

    # Clear the session
    session.clear()

    # If you're using Flask-Login, also log the user out using its function
    # logout_user()

    flash("Logged out successfully!", "success")
    # Redirect to the login page or any other page you desire
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
