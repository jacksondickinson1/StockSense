from app import app, load_inventory, save_inventory, find_item_by_id
from werkzeug.security import generate_password_hash, check_password_hash


# -------------------------
# Unit Tests
# -------------------------

def test_inventory_save_and_load():
    test_inventory = [
        {
            "id": "test-123",
            "name": "Test Sofa",
            "category": "Sofa",
            "color": "Gray",
            "size": "",
            "quantity": 5
        }
    ]

    save_inventory(test_inventory)
    inventory = load_inventory()

    assert len(inventory) >= 1
    assert inventory[0]["name"] == "Test Sofa"


def test_find_item_by_id():
    inventory = [
        {
            "id": "abc-123",
            "name": "Dining Table",
            "category": "Dining Table",
            "color": "Brown",
            "size": "",
            "quantity": 3
        }
    ]

    item = find_item_by_id(inventory, "abc-123")

    assert item is not None
    assert item["name"] == "Dining Table"


def test_password_hashing():
    password = "admin123"
    hashed = generate_password_hash(password)

    assert hashed != password
    assert check_password_hash(hashed, password)


def test_login_page_loads():
    client = app.test_client()
    response = client.get("/login")

    assert response.status_code == 200


def test_invalid_login_fails():
    client = app.test_client()

    response = client.post("/login", data={
        "username": "fakeuser",
        "password": "wrongpassword"
    }, follow_redirects=True)

    assert b"Invalid username or password" in response.data


def test_dashboard_redirects_when_not_logged_in():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 302
    assert "/login" in response.location


def test_employee_cannot_access_admin_panel():
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["username"] = "employee1"
        sess["role"] = "employee"

    response = client.get("/admin", follow_redirects=True)

    assert b"Access denied" in response.data


def test_negative_quantity_rejected():
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["username"] = "admin"
        sess["role"] = "admin"

    response = client.post("/add", data={
        "name": "Bad Item",
        "category": "Sofa",
        "color": "Black",
        "size": "",
        "quantity": "-5"
    }, follow_redirects=True)

    assert b"Quantity cannot be negative" in response.data


# -------------------------
# Route Integration Tests
# -------------------------

def test_route_login_authentication():
    client = app.test_client()

    response = client.post("/login", data={
        "username": "admin",
        "password": "admin123"
    }, follow_redirects=True)

    assert b"Furniture Inventory Dashboard" in response.data


def test_route_dashboard_load():
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["username"] = "admin"
        sess["role"] = "admin"

    response = client.get("/")

    assert response.status_code == 200
    assert b"Inventory" in response.data


def test_route_add_item():
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["username"] = "admin"
        sess["role"] = "admin"

    response = client.post("/add", data={
        "name": "Integration Test Sofa",
        "category": "Sofa",
        "color": "Gray",
        "size": "",
        "quantity": "7"
    }, follow_redirects=True)

    assert b"Item added successfully" in response.data


def test_route_update_quantity():
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["username"] = "admin"
        sess["role"] = "admin"

    client.post("/add", data={
        "name": "Update Test Chair",
        "category": "Chair",
        "color": "Black",
        "size": "",
        "quantity": "3"
    }, follow_redirects=True)

    inventory = load_inventory()
    item_id = inventory[-1]["id"]

    response = client.post(f"/update/{item_id}", data={
        "new_quantity": "10"
    }, follow_redirects=True)

    assert b"Item updated successfully" in response.data


def test_route_delete_item():
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["username"] = "admin"
        sess["role"] = "admin"

    client.post("/add", data={
        "name": "Delete Test Table",
        "category": "Dining Table",
        "color": "Brown",
        "size": "",
        "quantity": "2"
    }, follow_redirects=True)

    inventory = load_inventory()
    item_id = inventory[-1]["id"]

    response = client.get(f"/delete/{item_id}", follow_redirects=True)

    assert b"Item deleted" in response.data


def test_route_adjust_stock():
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["username"] = "admin"
        sess["role"] = "admin"

    client.post("/add", data={
        "name": "Adjust Test Recliner",
        "category": "Recliner",
        "color": "Tan",
        "size": "",
        "quantity": "5"
    }, follow_redirects=True)

    inventory = load_inventory()
    item_id = inventory[-1]["id"]

    with client.session_transaction() as sess:
        sess["username"] = "employee1"
        sess["role"] = "employee"

    response = client.get(f"/adjust/{item_id}/increase", follow_redirects=True)

    assert b"Inventory increased by 1" in response.data


def test_route_admin_create_user():
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["username"] = "admin"
        sess["role"] = "admin"

    response = client.post("/admin", data={
        "username": "integration_employee",
        "password": "test123",
        "role": "employee"
    }, follow_redirects=True)

    assert (
        b"User created successfully" in response.data
        or b"Username already exists" in response.data
    )


def test_route_delete_user():
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["username"] = "admin"
        sess["role"] = "admin"

    client.post("/admin", data={
        "username": "delete_me_employee",
        "password": "test123",
        "role": "employee"
    }, follow_redirects=True)

    response = client.get("/delete_user/delete_me_employee", follow_redirects=True)

    assert (
        b"User deleted successfully" in response.data
        or b"User not found" in response.data
    )
