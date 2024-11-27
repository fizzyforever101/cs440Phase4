import tkinter as tk
from tkinter import messagebox
import mysql.connector

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
        messagebox.showerror("Database Error", f"Error connecting to database:\n{e}")
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
        messagebox.showinfo("Success", f"Procedure {proc_name} executed successfully!")
    except mysql.connector.Error as e:
        messagebox.showerror("Execution Error", f"Error executing procedure:\n{e}")
    finally:
        conn.close()

# Handle dynamic form submission
def submit_form(proc_name, entries):
    try:
        params = [entry.get() for entry in entries]

        # Validation specific to `add_business` procedure
        if proc_name == "add_business":
            long_name, rating, spent, location = params
            if not long_name:
                raise ValueError("Business name cannot be empty.")
            if not rating.isdigit() or not (1 <= int(rating) <= 5):
                raise ValueError("Rating must be an integer between 1 and 5.")
            if not spent.isdigit() or int(spent) < 0:
                raise ValueError("Spent amount must be a non-negative integer.")
            if not location:
                raise ValueError("Location cannot be empty.")
        
        execute_procedure(proc_name, params)
    except ValueError as ve:
        messagebox.showerror("Validation Error", str(ve))

# Create dynamic form for a procedure
def open_procedure_form(proc_name, fields):
    # Create a new window for the form
    form_window = tk.Toplevel(root)
    form_window.title(f"Call Procedure: {proc_name}")
    
    tk.Label(form_window, text=f"Fill in parameters for {proc_name}", font=("Arial", 12)).pack(pady=10)

    entries = []
    for i, field in enumerate(fields):
        frame = tk.Frame(form_window)
        frame.pack(pady=5, padx=10, fill="x")

        tk.Label(frame, text=f"{field}:", width=15, anchor="w").pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(side="right", fill="x", expand=True)
        entries.append(entry)

    # Submit button
    tk.Button(
        form_window, 
        text="Submit", 
        command=lambda: submit_form(proc_name, entries)
    ).pack(pady=10)

# Main GUI setup
root = tk.Tk()
root.title("MySQL Procedure Executor")
root.geometry("400x300")

# Define stored procedures and their input fields
stored_procedures = {
    "add_business": ["long_name", "rating", "spent", "location"],
    # Add other procedures here if needed
}

# Main Frame for Layout
main_frame = tk.Frame(root)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

# Header label
tk.Label(main_frame, text="Available Procedures", font=("Arial", 14)).pack(pady=10)

# Create buttons for each stored procedure
for proc_name, fields in stored_procedures.items():
    tk.Button(
        main_frame,
        text=proc_name,
        command=lambda proc_name=proc_name, fields=fields: open_procedure_form(proc_name, fields),
        width=30
    ).pack(pady=5)

# Run the Tkinter main loop
root.mainloop()
