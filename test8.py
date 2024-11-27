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
        
        # Check if any rows were affected
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
    params = [entry.text() if isinstance(entry, QtWidgets.QLineEdit) else entry.currentText() if isinstance(entry, QComboBox) else entry.value() for entry in entries]
    execute_procedure(proc_name, params)

# Create dynamic form for a procedure
def open_procedure_form(proc_name, fields, dropdown_data=None, spinbox_limits=None):
    form_window = QtWidgets.QDialog()
    form_window.setWindowTitle(f"Call Procedure: {proc_name}")

    layout = QtWidgets.QFormLayout()

    entries = []
    for i, field in enumerate(fields):
        if field in dropdown_data:
            # Create a dropdown (QComboBox) for fields that have predefined options
            entry = QComboBox()
            entry.addItems(dropdown_data[field])
            layout.addRow(f"{field}:", entry)
        elif field == "employee_experience":
            # Create a spinbox for employee_experience to ensure it can only be an integer starting from 0
            entry = QSpinBox()
            entry.setMinimum(0)
            entry.setMaximum(100)  # Adjust max value if needed
            layout.addRow(f"{field}:", entry)
        else:
            # Create a text input field for other fields
            entry = QtWidgets.QLineEdit()
            layout.addRow(f"{field}:", entry)
        
        entries.append(entry)

    submit_button = QtWidgets.QPushButton("Submit")
    submit_button.clicked.connect(lambda: submit_form(proc_name, entries))
    layout.addRow(submit_button)

    form_window.setLayout(layout)
    form_window.exec_()

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
            "add_employee": ["username", "first_name", "last_name", "address", "birthdate", "taxID", "hired", "employee_experience", "salary"]
        }

        # Predefined dropdown data for 'license_type' and 'username' (for add_driver_role) and 'taxID' (for add_employee)
        self.dropdown_data = {
            "license_type": ["A", "B", "C", "D"],
            "username": self.get_usernames(),  # Allow users to input any username
            "taxID": self.get_taxIDs()  # Allow users to input any taxID
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
            button.clicked.connect(lambda _, proc_name=proc_name, fields=fields: open_procedure_form(proc_name, fields, self.dropdown_data))
            layout.addWidget(button)

        self.setLayout(layout)

    # Function to get available usernames for dropdown (for add_driver_role)
    def get_usernames(self):
        conn = connect_to_db()
        usernames = []
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM employees")
            usernames = [row[0] for row in cursor.fetchall()]
            conn.close()
        return usernames

    # Function to get available taxIDs for dropdown (for add_employee)
    def get_taxIDs(self):
        conn = connect_to_db()
        taxIDs = []
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT taxID FROM employees")
            taxIDs = [row[0] for row in cursor.fetchall()]
            conn.close()
        return taxIDs

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
