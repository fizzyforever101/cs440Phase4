import sys
from PyQt5 import QtWidgets, QtCore
import mysql.connector
from PyQt5.QtWidgets import QMessageBox, QSpinBox

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
    params = [entry.text() if isinstance(entry, QtWidgets.QLineEdit) else entry.value() if isinstance(entry, QSpinBox) else entry.text() for entry in entries]
    execute_procedure(proc_name, params)

# Create dynamic form for a procedure
def open_procedure_form(proc_name, fields):
    form_window = QtWidgets.QDialog()
    form_window.setWindowTitle(f"Call Procedure: {proc_name}")

    layout = QtWidgets.QFormLayout()

    entries = []
    for i, field in enumerate(fields):
        if field == "employee_experience" or field == "salary":
            # Create a spinbox for employee_experience and salary
            entry = QSpinBox()
            entry.setMinimum(0)
            entry.setMaximum(100000)  # Adjust max value as needed
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
