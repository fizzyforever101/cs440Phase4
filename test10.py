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
        elif isinstance(entry, QSpinBox):  # If it's a QSpinBox (e.g., for salary)
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
        if field == "username":  # Use a QComboBox for username (from DB)
            entry = QComboBox()
            usernames = get_usernames()  # Fetch usernames from the database
            entry.addItems(usernames)
            layout.addRow(f"{field}:", entry)
        elif field == "taxID":  # Use a QComboBox for taxID (from DB)
            entry = QComboBox()
            taxIDs = get_taxIDs()  # Fetch tax IDs from the database
            entry.addItems(taxIDs)
            layout.addRow(f"{field}:", entry)
        elif field == "salary":  # Use a QSpinBox for salary
            entry = QSpinBox()
            entry.setMinimum(0)
            entry.setMaximum(100000)  # Adjust max value as needed
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

# Get tax IDs from the database for dropdown (ComboBox)
def get_taxIDs():
    conn = connect_to_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT taxID FROM employees")  # Query to get taxIDs
        taxIDs = [row[0] for row in cursor.fetchall()]
        return taxIDs
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error fetching tax IDs from database:\n{e}")
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
            "add_employee": ["username", "first_name", "last_name", "address", "birthdate", "taxID", "hired", "employee_experience", "salary"]
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
