# StockSense
StockSense is a Flask-based inventory management system designed for furniture store operations. The application allows users to manage inventory, track stock levels, search and filter items, and control access using role-based permissions.

# StockSense
---

## Features

- Secure login system with password hashing
- Role-based access control (Admin and Employee)
- Add, update, delete, and adjust inventory
- Search and filter inventory items
- User management (admin only)
- JSON-based data persistence
- Input validation and error handling
- Automated testing using pytest

---

## Technologies Used

- Python
- Flask
- HTML / CSS
- JavaScript
- JSON (data storage)
- pytest (testing framework)
- Werkzeug (password hashing)

---

## Project Structure
StockSense/
├── app.py
├── inventory.json
├── users.json
├── test_stocksense.py
├── README.md
└── templates/
├── index.html
├── login.html
└── admin.html


---

## Setup Instructions

Follow these steps to set up and run the application:

### 1. Install Python
Ensure Python is installed on your system.

Check installation:
```bash
py --version

2. Download and extract the ZIP file. Open the StockSense folder in Visual Studio Code or another code editor.

3. Open Terminal

Navigate to the project directory:

cd path_to_StockSense

4. Install Dependencies

Install required packages:

py -m pip install flask
py -m pip install pytest

5. Run the Application

Start the Flask server:

copy py app.py and paste into terminal window in your code editor

You should see:

Running on http://127.0.0.1:5000/

6. Open in Browser

Go to:

http://127.0.0.1:5000/

Default Login Credentials

Admin Account:

Username: admin
Password: admin123

User Roles
Admin
Add inventory items
Update inventory quantities
Delete inventory items
Create users
Delete users
Adjust stock levels

Employee
View inventory
Search and filter items
Adjust stock levels
Cannot add/delete items
Cannot access admin panel


7. How to run tests:

Open Terminal in Project Folder
Make sure you are inside the main StockSense directory (the same folder as `app.py` and `test_stocksense.py`):
Install pytest (if not already installed)
py -m pip install pytest

To run all 16 test:

py -m pytest test_stocksense.py -v

Run a Specific Test

py -m pytest -k test_inventory_save_and_load -v

Testing Coverage

The test suite includes:

Unit Testing
Inventory save/load functionality
UUID item lookup
Password hashing
Login page loading
Invalid login rejection
Dashboard access protection
Role-based access control
Input validation
Integration Testing
Login route (authentication + session)
Dashboard loading
Add inventory item
Update item quantity
Delete item
Adjust stock levels
Create user
Delete user

Important Notes:
Ensure inventory.json and users.json are located in the root directory
Do not place test files inside the templates folder
If tests fail, verify dependencies are installed correctly
This project uses JSON for storage and is intended as a functional prototype
Summary

StockSense is a fully functional inventory management system demonstrating backend development, authentication, role-based access control, data persistence, and automated testing. The system has been tested using unit, integration, and security testing methods to ensure reliability and correctness.
