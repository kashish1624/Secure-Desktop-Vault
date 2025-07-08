# === utils.py ===

import sqlite3         # Used for database operations (SQLite)
import hashlib         # Used to hash passwords securely
import os              # Used to work with file paths
import sys             # Used to check if the app is running as .exe
import random          # Used to generate random passwords
import string          # Contains letters, digits, and symbols for password generation


def resource_path(relative_path):  # This function helps locate file paths
    try:
        base_path = sys._MEIPASS   # Used when running as a compiled .exe (PyInstaller)
    except Exception:
        base_path = os.path.abspath(".")  # Used when running normally as a .py file
    return os.path.join(base_path, relative_path)  # Combine base path and relative path


DB_PATH = resource_path("users.db")  # Set the full path to the SQLite database


def hash_password(password):  # Converts plain password into a secure hashed format
    return hashlib.sha256(password.encode()).hexdigest()  # Encode, hash using SHA256, return hex format


def user_exists(username):  # Checks whether a user already exists in the database
    conn = sqlite3.connect(DB_PATH)              # Connect to the database
    cursor = conn.cursor()                       # Create a cursor to execute SQL commands
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))  # Check for user
    exists = cursor.fetchone() is not None       # If data is found, user exists
    conn.close()                                 # Close database connection
    return exists                                # Return True or False


def generate_random_password(length=10):  # Generates a secure random password
    characters = string.ascii_letters + string.digits + string.punctuation  # All possible characters
    return ''.join(random.choice(characters) for _ in range(length))  # Randomly choose characters to form password
