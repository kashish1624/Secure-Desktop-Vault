# === crypto_util.py ===

from cryptography.fernet import Fernet  # Fernet is used for encrypting and decrypting files securely
import base64  # Used to convert binary key into readable format (needed by Fernet)
import hashlib  # Used to generate a strong key from a password or secret string

# This is a secret string used to generate a consistent encryption key
# In real applications, this should be kept hidden or in a secure place
SECRET = "this_is_a_strong_secret_key_used_for_encryption"

# A custom header added at the beginning of encrypted files
# Helps us identify whether a file is encrypted by this app
FILE_HEADER = b'SECUREVAULT'

# This function creates a Fernet-compatible key using SHA-256 and base64 encoding
def generate_key(secret: str) -> bytes:
    key = hashlib.sha256(secret.encode()).digest()  # Hash the secret to get a 32-byte key
    return base64.urlsafe_b64encode(key)  # Convert the key to base64 format (required by Fernet)

# Create a global Fernet object using the generated key so we can use it for encryption/decryption
fernet = Fernet(generate_key(SECRET))

# Function to encrypt a file in-place (overwrite original file with encrypted content)
def encrypt_file(path: str):
    with open(path, "rb") as f:  # Open the file in binary read mode
        data = f.read()  # Read the full content of the file
    
    encrypted = fernet.encrypt(data)  # Encrypt the content using Fernet

    with open(path, "wb") as f:  # Open the same file in binary write mode
        f.write(FILE_HEADER + encrypted)  # Write our custom header + encrypted content

# Function to decrypt a file (reads from one path and saves decrypted output to another)
def decrypt_file(enc_path: str, dec_path: str):
    with open(enc_path, "rb") as f:  # Open the encrypted file in binary read mode
        content = f.read()  # Read the entire encrypted content
    
    # Check if the file starts with our special header
    if not content.startswith(FILE_HEADER):
        raise ValueError("This file is not encrypted")  # Raise error if it's not a valid encrypted file

    encrypted_data = content[len(FILE_HEADER):]  # Remove the header to get only the encrypted data
    decrypted = fernet.decrypt(encrypted_data)  # Decrypt the encrypted part using Fernet

    with open(dec_path, "wb") as f:  # Open the output file in binary write mode
        f.write(decrypted)  # Write the decrypted content to the new file

