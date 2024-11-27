import sys
from PyQt5 import QtWidgets, QtCore
import mysql.connector
from PyQt5.QtWidgets import QMessageBox, QComboBox, QSpinBox

# Database connection setup
def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="t00r1234",
            database="business_supply"
        )
        return conn
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error connecting to database:\n{e}")
        return None

# Execute stored procedure
def execute_procedure(proc_name, params):
    conn = connect_to_db()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        cursor.execute(f"CALL {proc_name}({', '.join(['%s'] * len(params))})", params)
        conn.commit()

        # Check if any rows were affected by the procedure
        if cursor.rowcount > 0:
            QMessageBox.information(None, "Success", f"Procedure {proc_name} executed successfully!")
        else:
            QMessageBox.information(None, "No Change", "No rows were affected by the procedure.")
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Execution Error", f"Error executing procedure:\n{e}")
    finally:
        conn.close()

# Handle dynamic form submission
def submit_form(proc_name, entries):
    # Validate inputs
    params = []
    for entry in entries:
        if isinstance(entry, QComboBox):  # If it's a dropdown (QComboBox), get the selected item
            params.append(entry.currentText())
        elif isinstance(entry, QSpinBox):  # If it's a QSpinBox (e.g., for driver_experience)
            params.append(entry.value())
        else:  # Otherwise, it's a QLineEdit
            if entry.text().strip() == "":  # Check for empty inputs
                QMessageBox.warning(None, "Input Error", f"Please fill in all fields.")
                return
            params.append(entry.text())

    execute_procedure(proc_name, params)

# Create dynamic form for a procedure
def open_procedure_form(proc_name, fields):
    form_window = QtWidgets.QDialog()
    form_window.setWindowTitle(f"Call Procedure: {proc_name}")

    layout = QtWidgets.QFormLayout()

    entries = []
    for field in fields:
        if field == "rating":  # Use a QComboBox for rating
            entry = QComboBox()
            entry.addItems([str(i) for i in range(1, 6)])  # Add ratings 1-5
            layout.addRow(f"{field}:", entry)
        elif field == "location":  # Use a QComboBox for location (assuming locations are predefined)
            entry = QComboBox()
            locations = get_locations()  # Fetch locations from the database
            entry.addItems(locations)
            layout.addRow(f"{field}:", entry)
        elif field == "home_base":  # Use a QComboBox for location (assuming locations are predefined)
            entry = QComboBox()
            locations = get_locations()  # Fetch locations from the database
            entry.addItems(locations)
            layout.addRow(f"{field}:", entry)
        elif field == "destination":  # Use a QComboBox for location (assuming locations are predefined)
            entry = QComboBox()
            locations = get_locations()  # Fetch locations from the database
            entry.addItems(locations)
            layout.addRow(f"{field}:", entry)
        elif field == "manager":  # Use a QComboBox for location (assuming locations are predefined)
            entry = QComboBox()
            employees = get_employees()  # Fetch locations from the database
            entry.addItems(employees)
            layout.addRow(f"{field}:", entry)
        elif field == "license_type":  # Use a QComboBox for license_type
            entry = QComboBox()
            license_types = get_license_types()  # Fetch license types from the database
            entry.addItems(license_types)
            layout.addRow(f"{field}:", entry)
        elif field == "username":  # Use a QComboBox for username
            entry = QComboBox()
            usernames = get_usernames()  # Fetch usernames from the database
            entry.addItems(usernames)
            layout.addRow(f"{field}:", entry)
        elif field == "van_id":  # Use a QComboBox for username
            entry = QComboBox()
            delivery_service_ids = get_delivery_service_ids()  # Fetch usernames from the database
            entry.addItems(delivery_service_ids)
            layout.addRow(f"{field}:", entry)
        elif field == "driver_experience":  # Use a QSpinBox for driver experience (integer field)
            entry = QSpinBox()
            entry.setRange(0, 100)  # Assuming experience ranges from 0 to 100
            entry.setValue(0)  # Set the initial value to 0
            layout.addRow(f"{field}:", entry)
        elif field == "salary":  # Use a QSpinBox for salary
            entry = QSpinBox()
            entry.setMinimum(0)
            entry.setMaximum(100000)  # Adjust max value as needed
            layout.addRow(f"{field}:", entry)
        elif field == "spent":  # Use a QSpinBox for salary
            entry = QSpinBox()
            entry.setMinimum(0)
            entry.setMaximum(100000)  # Adjust max value as needed
            layout.addRow(f"{field}:", entry)
        elif field == "employee_experience":  # Use a QSpinBox for employee_experience
            entry = QSpinBox()
            entry.setRange(0, 100)  # Assuming experience ranges from 0 to 100
            entry.setValue(0)  # Set the initial value to 0
            layout.addRow(f"{field}:", entry)
        elif field == "space":  # Use a QSpinBox for employee_experience
            entry = QSpinBox()
            entry.setRange(0, 100)  # Assuming experience ranges from 0 to 100
            entry.setValue(0)  # Set the initial value to 0
            layout.addRow(f"{field}:", entry)
        elif field == "x_coord":  # Use a QSpinBox for employee_experience
            entry = QSpinBox()
            entry.setRange(0, 1000)  # Assuming experience ranges from 0 to 100
            entry.setValue(0)  # Set the initial value to 0
            layout.addRow(f"{field}:", entry)
        elif field == "y_coord":  # Use a QSpinBox for employee_experience
            entry = QSpinBox()
            entry.setRange(0, 1000)  # Assuming experience ranges from 0 to 100
            entry.setValue(0)  # Set the initial value to 0
            layout.addRow(f"{field}:", entry)
        elif field == "weight":  # Use a QSpinBox for employee_experience
            entry = QSpinBox()
            entry.setRange(0, 1000)  # Assuming experience ranges from 0 to 100
            entry.setValue(0)  # Set the initial value to 0
            layout.addRow(f"{field}:", entry)
        elif field == "tag":  # Use a QSpinBox for employee_experience
            entry = QSpinBox()
            entry.setRange(0, 10000)  # Assuming experience ranges from 0 to 100
            entry.setValue(0)  # Set the initial value to 0
            layout.addRow(f"{field}:", entry)
        elif field == "capacity":  # Use a QSpinBox for employee_experience
            entry = QSpinBox()
            entry.setRange(0, 10000)  # Assuming experience ranges from 0 to 100
            entry.setValue(0)  # Set the initial value to 0
            layout.addRow(f"{field}:", entry)
        elif field == "sales":  # Use a QSpinBox for employee_experience
            entry = QSpinBox()
            entry.setRange(0, 100000)  # Assuming experience ranges from 0 to 100
            entry.setValue(0)  # Set the initial value to 0
            layout.addRow(f"{field}:", entry)
        elif field == "fuel":  # Use a QSpinBox for employee_experience
            entry = QSpinBox()
            entry.setRange(0, 100000)  # Assuming experience ranges from 0 to 100
            entry.setValue(0)  # Set the initial value to 0
            layout.addRow(f"{field}:", entry)
        else:  # Use a QLineEdit for other fields
            entry = QtWidgets.QLineEdit()
            layout.addRow(f"{field}:", entry)

        entries.append(entry)

    submit_button = QtWidgets.QPushButton("Submit")
    submit_button.clicked.connect(lambda _, proc_name=proc_name, entries=entries: submit_form(proc_name, entries))
    layout.addRow(submit_button)

    form_window.setLayout(layout)
    form_window.exec_()

# Get locations from the database for dropdown (ComboBox)
def get_locations():
    conn = connect_to_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT label FROM locations")  # Query to get locations
        locations = [row[0] for row in cursor.fetchall()]
        return locations
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error fetching locations from database:\n{e}")
        return []
    finally:
        conn.close()

def get_delivery_service_ids():
    conn = connect_to_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM delivery_services")  # Query to get locations
        locations = [row[0] for row in cursor.fetchall()]
        return locations
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error fetching locations from database:\n{e}")
        return []
    finally:
        conn.close()

def get_employees():
    conn = connect_to_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM employees")  # Query to get locations
        locations = [row[0] for row in cursor.fetchall()]
        return locations
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error fetching locations from database:\n{e}")
        return []
    finally:
        conn.close()

# Get license types from the database for dropdown (ComboBox)
def get_license_types():
    conn = connect_to_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT license_type FROM drivers")  # Query to get license types
        license_types = [row[0] for row in cursor.fetchall()]
        return license_types
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error fetching license types from database:\n{e}")
        return []
    finally:
        conn.close()

# Get usernames from the database for dropdown (ComboBox)
def get_usernames():
    conn = connect_to_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM employees")  # Query to get usernames
        usernames = [row[0] for row in cursor.fetchall()]
        return usernames
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error fetching usernames from database:\n{e}")
        return []
    finally:
        conn.close()

# Main GUI setup
class MyApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MySQL Procedure Executor")
        self.setGeometry(100, 100, 400, 300)

        # Define stored procedures and their input fields
        self.stored_procedures = {
            "add_business": ["long_name", "rating", "spent", "location"],
            "add_driver_role": ["username", "licenseID", "license_type", "driver_experience"],
            "add_employee": ["employee_username", "first_name", "last_name", "address", "birthdate", "taxID", "hired", "employee_experience", "salary"],
            "add_location": ["label", "x_coord", "y_coord", "space"],
            "add_owner": ["owner_username", "first_name", "last_name", "address", "birthdate"],
            "add_product": ["barcode", "name", "weight"],
            "add_service": ["id", "long_name", "home_base", "manager"],
            "add_van": ["van_id", "tag", "fuel", "capacity", "sales", "driven_by"],
            "add_worker_role": ["username"],
            "drive_van": ["id", "tag", "destination"]
            # Add other procedures here if needed
        }

        # Create layout
        layout = QtWidgets.QVBoxLayout()

        # Title
        title_label = QtWidgets.QLabel("Available Procedures")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)

        # Create buttons for each stored procedure
        for proc_name, fields in self.stored_procedures.items():
            button = QtWidgets.QPushButton(proc_name)
            button.clicked.connect(lambda _, proc_name=proc_name, fields=fields: open_procedure_form(proc_name, fields))
            layout.addWidget(button)

        self.setLayout(layout)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
