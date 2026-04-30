from flask import Flask, render_template, request, redirect, flash
import json
import os

app = Flask(__name__)
app.secret_key = "stocksense_secret"

DATA_FILE = "inventory.json"


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


@app.route("/")
def home():
    inventory = load_inventory()
    return render_template("index.html", inventory=inventory)


@app.route("/add", methods=["POST"])
def add_item():
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
        flash("Mattress size is required when category is Mattress.")
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
    flash("Item added successfully!")

    return redirect("/")


@app.route("/update/<int:index>", methods=["POST"])
def update_item(index):
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
        flash("Item updated successfully!")

    return redirect("/")


@app.route("/adjust/<int:index>/<action>")
def adjust_item(index, action):
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
    inventory = load_inventory()

    if 0 <= index < len(inventory):
        inventory.pop(index)
        save_inventory(inventory)
        flash("Item deleted.")

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
