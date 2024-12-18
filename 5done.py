import sys
from PyQt5 import QtWidgets, QtCore
import mysql.connector
from PyQt5.QtWidgets import QMessageBox, QComboBox, QSpinBox, QScrollArea, QTableWidget, QTableWidgetItem, QVBoxLayout, QDialog

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

def execute_view(view_name):
    conn = connect_to_db()
    if conn is None:
        return
    
    try:
        cursor = conn.cursor()
        # Execute the query to fetch all data from the view
        cursor.execute(f"SELECT * FROM {view_name}")
        
        # Fetch column names (from cursor.description)
        column_names = [desc[0] for desc in cursor.description]
        
        # Fetch results
        results = cursor.fetchall()
        
        # Check if results are returned
        if results:
            # Handle the results: Show them in a table pop-up
            show_table_popup(results, column_names)
            QMessageBox.information(None, "Success", f"View {view_name} executed successfully!")
        else:
            QMessageBox.information(None, "No Results", "No rows found in the view.")
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Execution Error", f"Error executing view:\n{e}")
    finally:
        conn.close()

def show_table_popup(data, column_names):
    # Create a pop-up window to display the data in a table
    table_popup = TablePopUp(data, column_names)
    table_popup.exec_()

class TablePopUp(QDialog):
    def __init__(self, data, column_names):
        super().__init__()
        self.setWindowTitle("Data Table")

        # Set up the layout
        layout = QVBoxLayout()

        # Create a QTableWidget to display the data
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Populate the table with data
        self.populate_table(data, column_names)

        # Set the layout for the dialog
        self.setLayout(layout)

    def populate_table(self, data, column_names):
        # Set the row count based on the number of rows in the data
        self.table_widget.setRowCount(len(data))
        
        # Set the column count (based on the number of columns in the data)
        self.table_widget.setColumnCount(len(column_names))

        # Set the column headers (column names)
        self.table_widget.setHorizontalHeaderLabels(column_names)

        # Populate the table with data
        for row in range(len(data)):
            for col in range(len(data[row])):
                self.table_widget.setItem(row, col, QTableWidgetItem(str(data[row][col])))

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
        elif field == "business_long_name":  # Use a QComboBox for location (assuming locations are predefined)
            entry = QComboBox()
            locations = get_business_long_names()  # Fetch locations from the database
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
        elif field == "employee_username":  # Use a QComboBox for username
            entry = QComboBox()
            usernames = get_employee_usernames()  # Fetch usernames from the database
            entry.addItems(usernames)
            layout.addRow(f"{field}:", entry)
        elif field == "van_id":  # Use a QComboBox for username
            entry = QComboBox()
            delivery_service_ids = get_delivery_service_ids()  # Fetch usernames from the database
            entry.addItems(delivery_service_ids)
            layout.addRow(f"{field}:", entry)
        elif field == "van_tag":  # Use a QComboBox for username
            entry = QComboBox()
            delivery_service_ids = get_van_tags()  # Fetch usernames from the database
            entry.addItems(delivery_service_ids)
            layout.addRow(f"{field}:", entry)
        elif field == "new_employee_id":  # Use a QComboBox for username
            entry = QComboBox()
            delivery_service_ids = get_delivery_service_ids()  # Fetch usernames from the database
            entry.addItems(delivery_service_ids)
            layout.addRow(f"{field}:", entry)
        elif field == "driver_username":  # Use a QComboBox for username
            entry = QComboBox()
            delivery_service_ids = get_driver_usernames()  # Fetch usernames from the database
            entry.addItems(delivery_service_ids)
            layout.addRow(f"{field}:", entry)
        elif field == "employee_id":  # Use a QComboBox for username
            entry = QComboBox()
            delivery_service_ids = get_employee_ids()  # Fetch usernames from the database
            entry.addItems(delivery_service_ids)
            layout.addRow(f"{field}:", entry)
        elif field == "owner":  # Use a QComboBox for username
            entry = QComboBox()
            delivery_service_ids = get_owners()  # Fetch usernames from the database
            entry.addItems(delivery_service_ids)
            layout.addRow(f"{field}:", entry)
        elif field == "product_barcode":  # Use a QComboBox for username
            entry = QComboBox()
            delivery_service_ids = get_barcodes()  # Fetch usernames from the database
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
        elif field == "quantity":  # Use a QSpinBox for employee_experience
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
        elif field == "price":  # Use a QSpinBox for employee_experience
            entry = QSpinBox()
            entry.setRange(0, 1000)  # Assuming experience ranges from 0 to 100
            entry.setValue(0)  # Set the initial value to 0
            layout.addRow(f"{field}:", entry)
        elif field == "more_packages":  # Use a QSpinBox for employee_experience
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
        elif field == "more_fuel":  # Use a QSpinBox for employee_experience
            entry = QSpinBox()
            entry.setRange(0, 100000)  # Assuming experience ranges from 0 to 100
            entry.setValue(0)  # Set the initial value to 0
            layout.addRow(f"{field}:", entry)
        elif field == "amount":  # Use a QSpinBox for employee_experience
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

def get_van_tags():
    conn = connect_to_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT distinct tag FROM vans")  # Query to get locations
        locations = [str(row[0]) for row in cursor.fetchall()]
        return locations
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error fetching locations from database:\n{e}")
        return []
    finally:
        conn.close()

def get_owners():
    conn = connect_to_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username tag FROM business_owners")  # Query to get locations
        locations = [str(row[0]) for row in cursor.fetchall()]
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

def get_driver_usernames():
    conn = connect_to_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM drivers")  # Query to get locations
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

def get_barcodes():
    conn = connect_to_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT barcode FROM products")  # Query to get usernames
        usernames = [row[0] for row in cursor.fetchall()]
        return usernames
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error fetching usernames from database:\n{e}")
        return []
    finally:
        conn.close()

def get_employee_usernames():
    conn = connect_to_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM work_for")  # Query to get usernames
        usernames = [row[0] for row in cursor.fetchall()]
        return usernames
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error fetching usernames from database:\n{e}")
        return []
    finally:
        conn.close()

def get_business_long_names():
    conn = connect_to_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT long_name FROM businesses")  # Query to get usernames
        usernames = [row[0] for row in cursor.fetchall()]
        return usernames
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error fetching usernames from database:\n{e}")
        return []
    finally:
        conn.close()

def get_employee_ids():
    conn = connect_to_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT distinct id FROM work_for")  # Query to get usernames
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
        self.setWindowTitle("MySQL Procedure/View Executor")
        self.setGeometry(100, 100, 400, 300)

        # Define stored procedures and their input fields
        self.stored_procedures = {
            "add_business": ["long_name", "rating", "spent", "location"],
            "add_driver_role": ["username", "licenseID", "license_type", "driver_experience"],
            "add_employee": ["employee's_username", "first_name", "last_name", "address", "birthdate", "taxID", "hired", "employee_experience", "salary"],
            "add_location": ["label", "x_coord", "y_coord", "space"],
            "add_owner": ["owner_username", "first_name", "last_name", "address", "birthdate"],
            "add_product": ["barcode", "name", "weight"],
            "add_service": ["id", "long_name", "home_base", "manager"],
            "add_van": ["van_id", "tag", "fuel", "capacity", "sales", "driven_by"],
            "add_worker_role": ["username"],
            "drive_van": ["id", "tag", "destination"],
            "fire_employee": ["employee_username", "employee_id"],
            "hire_employee": ["username", "new_employee_id"],
            "load_van": ["van_id", "tag", "product_barcode", "price", "more_packages"],
            "manage_service": ["employee_username", "employee_id"],
            "purchase_product": ["business_long_name", "van_id", "van_tag", "product_barcode", "quantity"],
            "refuel_van": ["van_id", "van_tag", "more_fuel"],
            "remove_driver_role": ["driver_username"],
            "remove_product": ["product_barcode"],
            "remove_van": ["van_id", "van_tag"],
            "start_funding": ["owner", "amount", "business_long_name", "fund_date"],
            "takeover_van": ["driver_username", "van_id", "van_tag"]
            # Add other procedures here if needed
        }

        self.views = ["display_driver_view", "display_employee_view", "display_location_view", "display_owner_view", "display_product_view", "display_service_view"]

        # Create layout
        self.layout = QtWidgets.QVBoxLayout()
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget) 

        # Title
        title_label = QtWidgets.QLabel("Available Procedures & Views")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(title_label)

        # Create buttons for each stored procedure
        for proc_name, fields in self.stored_procedures.items():
            button = QtWidgets.QPushButton(proc_name)
            button.clicked.connect(lambda _, proc_name=proc_name, fields=fields: open_procedure_form(proc_name, fields))
            self.content_layout.addWidget(button)

        for view_name in self.views:
            button = QtWidgets.QPushButton(view_name)
            button.clicked.connect(lambda _, view_name=view_name: execute_view(view_name))
            self.content_layout.addWidget(button)

        self.scroll_area.setWidget(self.content_widget)

        # Add the scroll area to the main layout
        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
