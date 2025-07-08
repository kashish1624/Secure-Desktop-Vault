# 🔐 Secure Vault - Final Working login_window.py (fixed to open dashboard)

# ======== IMPORTS ========
import tkinter as tk  # Used to build the GUI (buttons, labels, input fields)
from tkinter import messagebox, simpledialog  # For popup alerts and input boxes
import sqlite3  # To connect and manage SQLite database
import hashlib  # For password hashing (security)
import os  # To handle file paths
import sys  # Used for correct file access (important for .exe)
import dashboard  # Import the dashboard to open after login

# ======== UTILITY FUNCTION ========
def resource_path(relative_path):
    # Finds correct path of files (helps when app is converted to .exe)
    try:
        base_path = sys._MEIPASS  # Used when running from .exe
    except Exception:
        base_path = os.path.abspath(".")  # Used during normal development
    return os.path.join(base_path, relative_path)  # Combines folder path with filename

# ======== PASSWORD HASHING ========
def hash_password(password):
    # Converts normal password into a secure hashed string
    return hashlib.sha256(password.encode()).hexdigest()

# ======== DATABASE SETUP ========
def init_db():
    # Initializes or creates the users database
    db_path = resource_path("users.db")  # Get the correct file path
    print("Looking for users.db at:", db_path)  # Helps debug location issue

    conn = sqlite3.connect(db_path)  # Connect to database
    c = conn.cursor()  # Create cursor to run SQL commands
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')  # Create table if not already there
    conn.commit()  # Save changes
    conn.close()  # Close connection

# ======== REGISTER A NEW USER ========
def register_user(username, password):
    # Tries to add a new user with hashed password
    conn = sqlite3.connect(resource_path("users.db"))
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True  # Registration successful
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

# ======== VALIDATE LOGIN CREDENTIALS ========
def validate_user(username, password):
    # Checks if username and password match
    conn = sqlite3.connect(resource_path("users.db"))
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    row = c.fetchone()  # Get one matching row
    conn.close()
    return row and row[0] == hash_password(password)  # Return True if password matches

# ======== RESET USER PASSWORD ========
def reset_password(username, new_password):
    # Updates password for a user (after forgot password)
    conn = sqlite3.connect(resource_path("users.db"))
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE username=?", (hash_password(new_password), username))
    conn.commit()
    conn.close()

# ======== CHECK IF USER EXISTS ========
def user_exists(username):
    # Returns True if username is found in database
    conn = sqlite3.connect(resource_path("users.db"))
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username=?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# ======== OPEN DASHBOARD AFTER LOGIN ========
def open_dashboard(username):
    # Save the username to a file for use in dashboard
    with open(".logged_in_user", "w") as f:
        f.write(username)

    login_win.destroy()  # Close the login window

    import dashboard
    dashboard.open_dashboard_window(username)  # Open dashboard with username

# ======== GUI FUNCTION - LOGIN BUTTON ========
def attempt_login():
    username = username_entry.get()  # Get entered username
    password = password_entry.get()  # Get entered password
    if validate_user(username, password):  # Check if login is valid
        open_dashboard(username)  # Open dashboard if correct
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")  # Show error

# ======== GUI FUNCTION - REGISTER BUTTON ========
def attempt_register():
    username = username_entry.get()
    password = password_entry.get()
    if register_user(username, password):  # Try to register
        messagebox.showinfo("Success", "User registered successfully.")  # Show success message
    else:
        messagebox.showwarning("Failed", "Username already exists.")  # Show warning

# ======== GUI FUNCTION - FORGOT PASSWORD BUTTON ========
def forgot_password():
    username = simpledialog.askstring("Recover Password", "Enter your username")  # Ask for username
    if username and user_exists(username):  # If user exists
        new_password = simpledialog.askstring("New Password", "Enter new password")  # Ask for new password
        if new_password:
            reset_password(username, new_password)  # Update password
            messagebox.showinfo("Success", "Password reset successfully.")
    else:
        messagebox.showerror("Error", "User not found")  # If user doesn't exist

# ======== CREATE LOGIN WINDOW ========
login_win = tk.Tk()  # Create the main login window
login_win.title("\U0001F510 Secure Vault Login")  # Title with lock emoji
login_win.geometry("300x250")  # Window size

init_db()  # Create users table if not present

# ======== FORM FRAME (USERNAME + PASSWORD FIELDS) ========
frame = tk.Frame(login_win)  # Create a container box
frame.pack(pady=30)  # Add space above and below the frame

# Label and Entry for Username
tk.Label(frame, text="Username:").grid(row=0, column=0, sticky="w")  # Text label
username_entry = tk.Entry(frame)  # Input box
username_entry.grid(row=0, column=1)  # Place in 1st row, 2nd column

# Label and Entry for Password
tk.Label(frame, text="Password:").grid(row=1, column=0, sticky="w")  # Text label
password_entry = tk.Entry(frame, show="*")  # Password input (masked with *)
password_entry.grid(row=1, column=1)

# ======== BUTTONS (LOGIN, REGISTER, FORGOT PASSWORD) ========
tk.Button(login_win, text="Login", command=attempt_login).pack(pady=5)  # Login button
tk.Button(login_win, text="Register", command=attempt_register).pack(pady=5)  # Register button
tk.Button(login_win, text="Forgot Password", command=forgot_password).pack(pady=5)  # Forgot Password button

# ======== RUN THE APP ========
login_win.mainloop()  # Keep the window open and wait for user actions
