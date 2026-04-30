from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import json
import os
import uuid

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
            inventory = json.load(file)
    except json.JSONDecodeError:
        return []

    changed = False
    for item in inventory:
        if "id" not in item:
            item["id"] = str(uuid.uuid4())
            changed = True

    if changed:
        save_inventory(inventory)

    return inventory


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
        users.append({
            "username": "admin",
            "password": generate_password_hash("admin123"),
            "role": "admin"
        })
        save_users(users)


def is_logged_in():
    return "username" in session


def is_admin():
    return session.get("role") == "admin"


def find_item_by_id(inventory, item_id):
    for item in inventory:
        if item.get("id") == item_id:
            return item
    return None


create_default_admin()


@app.route("/")
def home():
    if not is_logged_in():
        return redirect("/login")

    inventory = load_inventory()

    search = request.args.get("search", "").lower()
    category_filter = request.args.get("category", "")
    color_filter = request.args.get("color", "").lower()
    status_filter = request.args.get("status", "")

    filtered_inventory = []

    for item in inventory:
        name_match = search in item.get("name", "").lower()
        category_match = category_filter == "" or item.get("category", "") == category_filter
        color_match = color_filter == "" or color_filter in item.get("color", "").lower()

        if status_filter == "low":
            status_match = item.get("quantity", 0) <= 5
        elif status_filter == "in":
            status_match = item.get("quantity", 0) > 5
        else:
            status_match = True

        if name_match and category_match and color_match and status_match:
            filtered_inventory.append(item)

    return render_template(
        "index.html",
        inventory=filtered_inventory,
        username=session["username"],
        role=session["role"],
        search=search,
        category_filter=category_filter,
        color_filter=color_filter,
        status_filter=status_filter
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
                session["role"] = user.get("role", "employee")

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

        users.append({
            "username": username,
            "password": generate_password_hash(password),
            "role": role
        })

        save_users(users)
        flash("User created successfully.")
        return redirect("/admin")

    return render_template("admin.html", users=users, username=session["username"])


@app.route("/delete_user/<username>")
def delete_user(username):
    if not is_logged_in():
        return redirect("/login")

    if not is_admin():
        flash("Access denied. Admin privileges are required.")
        return redirect("/")

    users = load_users()

    if username == session["username"]:
        flash("You cannot delete your own account while logged in.")
        return redirect("/admin")

    updated_users = [user for user in users if user["username"] != username]

    if len(updated_users) == len(users):
        flash("User not found.")
    else:
        save_users(updated_users)
        flash("User deleted successfully.")

    return redirect("/admin")


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
        "id": str(uuid.uuid4()),
        "name": name,
        "category": category,
        "color": color,
        "size": size,
        "quantity": quantity
    })

    save_inventory(inventory)
    flash("Item added successfully.")
    return redirect("/")


@app.route("/update/<item_id>", methods=["POST"])
def update_item(item_id):
    if not is_logged_in():
        return redirect("/login")

    if not is_admin():
        flash("Only admins can manually update inventory quantities.")
        return redirect("/")

    inventory = load_inventory()
    item = find_item_by_id(inventory, item_id)

    if item is None:
        flash("Item not found.")
        return redirect("/")

    try:
        new_quantity = int(request.form["new_quantity"])
    except ValueError:
        flash("Quantity must be a number.")
        return redirect("/")

    if new_quantity < 0:
        flash("Quantity cannot be negative.")
        return redirect("/")

    item["quantity"] = new_quantity
    save_inventory(inventory)
    flash("Item updated successfully.")
    return redirect("/")


@app.route("/adjust/<item_id>/<action>")
def adjust_item(item_id, action):
    if not is_logged_in():
        return redirect("/login")

    inventory = load_inventory()
    item = find_item_by_id(inventory, item_id)

    if item is None:
        flash("Item not found.")
        return redirect("/")

    if action == "decrease":
        if item["quantity"] > 0:
            item["quantity"] -= 1
            flash("Inventory decreased by 1.")
        else:
            flash("Quantity cannot go below zero.")

    elif action == "increase":
        item["quantity"] += 1
        flash("Inventory increased by 1.")

    save_inventory(inventory)
    return redirect("/")


@app.route("/delete/<item_id>")
def delete_item(item_id):
    if not is_logged_in():
        return redirect("/login")

    if not is_admin():
        flash("Only admins can delete inventory items.")
        return redirect("/")

    inventory = load_inventory()

    updated_inventory = [item for item in inventory if item.get("id") != item_id]

    if len(updated_inventory) == len(inventory):
        flash("Item not found.")
    else:
        save_inventory(updated_inventory)
        flash("Item deleted.")

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
