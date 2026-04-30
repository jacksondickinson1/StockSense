from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import json
import os

app = Flask(__name__)
app.secret_key = "stocksense_secret"
app.permanent_session_lifetime = timedelta(minutes=30)

DATA_FILE = "inventory.json"
USER_FILE = "users.json"


def load_inventory():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_inventory(inventory):
    with open(DATA_FILE, "w") as file:
        json.dump(inventory, file, indent=4)


def load_users():
    if not os.path.exists(USER_FILE):
        return []

    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)


def create_default_admin():
    users = load_users()

    if len(users) == 0:
        admin_user = {
            "username": "admin",
            "password": generate_password_hash("admin123"),
            "role": "admin"
        }
        users.append(admin_user)
        save_users(users)


def is_logged_in():
    return "username" in session


def is_admin():
    return session.get("role") == "admin"


create_default_admin()


@app.route("/")
def home():
    if not is_logged_in():
        return redirect("/login")

    inventory = load_inventory()

    return render_template(
        "index.html",
        inventory=inventory,
        username=session["username"],
        role=session["role"]
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()

        username = request.form["username"].strip()
        password = request.form["password"].strip()

        for user in users:
            if user["username"] == username and check_password_hash(user["password"], password):
                session.permanent = True
                session["username"] = username
                session["role"] = user["role"]

                flash("Logged in successfully.")
                return redirect("/")

        flash("Invalid username or password.")
        return redirect("/login")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect("/login")


@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if not is_logged_in():
        return redirect("/login")

    if not is_admin():
        flash("Access denied. Admin privileges are required.")
        return redirect("/")

    users = load_users()

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        role = request.form["role"].strip()

        if username == "" or password == "":
            flash("Username and password are required.")
            return redirect("/admin")

        if role not in ["admin", "employee"]:
            flash("Invalid role selected.")
            return redirect("/admin")

        for user in users:
            if user["username"] == username:
                flash("Username already exists.")
                return redirect("/admin")

        new_user = {
            "username": username,
            "password": generate_password_hash(password),
            "role": role
        }

        users.append(new_user)
        save_users(users)

        flash("User created successfully.")
        return redirect("/admin")

    return render_template("admin.html", users=users, username=session["username"])


@app.route("/add", methods=["POST"])
def add_item():
    if not is_logged_in():
        return redirect("/login")

    if not is_admin():
        flash("Only admins can add inventory items.")
        return redirect("/")

    inventory = load_inventory()

    name = request.form["name"].strip()
    category = request.form["category"].strip()
    color = request.form["color"].strip()
    size = request.form.get("size", "").strip()

    try:
        quantity = int(request.form["quantity"])
    except ValueError:
        flash("Quantity must be a number.")
        return redirect("/")

    if name == "":
        flash("Item name cannot be empty.")
        return redirect("/")

    if category == "":
        flash("Category cannot be empty.")
        return redirect("/")

    if color == "":
        flash("Color cannot be empty.")
        return redirect("/")

    if category == "Mattress" and size == "":
        flash("Mattress size is required.")
        return redirect("/")

    if category != "Mattress":
        size = ""

    if quantity < 0:
        flash("Quantity cannot be negative.")
        return redirect("/")

    inventory.append({
        "name": name,
        "category": category,
        "color": color,
        "size": size,
        "quantity": quantity
    })

    save_inventory(inventory)
    flash("Item added successfully.")
    return redirect("/")


@app.route("/update/<int:index>", methods=["POST"])
def update_item(index):
    if not is_logged_in():
        return redirect("/login")

    if not is_admin():
        flash("Only admins can manually update inventory quantities.")
        return redirect("/")

    inventory = load_inventory()

    try:
        new_quantity = int(request.form["new_quantity"])
    except ValueError:
        flash("Quantity must be a number.")
        return redirect("/")

    if new_quantity < 0:
        flash("Quantity cannot be negative.")
        return redirect("/")

    if 0 <= index < len(inventory):
        inventory[index]["quantity"] = new_quantity
        save_inventory(inventory)
        flash("Item updated successfully.")

    return redirect("/")


@app.route("/adjust/<int:index>/<action>")
def adjust_item(index, action):
    if not is_logged_in():
        return redirect("/login")

    inventory = load_inventory()

    if 0 <= index < len(inventory):
        if action == "decrease":
            if inventory[index]["quantity"] > 0:
                inventory[index]["quantity"] -= 1
                flash("Inventory decreased by 1.")
            else:
                flash("Quantity cannot go below zero.")

        elif action == "increase":
            inventory[index]["quantity"] += 1
            flash("Inventory increased by 1.")

        save_inventory(inventory)

    return redirect("/")


@app.route("/delete/<int:index>")
def delete_item(index):
    if not is_logged_in():
        return redirect("/login")

    if not is_admin():
        flash("Only admins can delete inventory items.")
        return redirect("/")

    inventory = load_inventory()

    if 0 <= index < len(inventory):
        inventory.pop(index)
        save_inventory(inventory)
        flash("Item deleted.")

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
