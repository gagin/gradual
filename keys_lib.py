import os
from cryptography.fernet import Fernet

def init():
    """
    Initializes the encryption key. Loads it from the environment variable if it exists,
    otherwise generates a new key and sets it as an environment variable.
    """
    key_str = os.environ.get("PY_ENCRYPTION_KEY")
    if key_str is None:
        key = Fernet.generate_key()
        key_str = key.decode("utf-8")
        os.environ["PY_ENCRYPTION_KEY"] = key_str
    return key_str.encode("utf-8")

def encrypt_data(data, key=None):
    """
    Encrypts the provided data using the encryption key and returns the encrypted data.
    If the key is not provided, it will be initialized from the environment.
    """
    if key is None:
        key = init()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data)
    return encrypted_data

def decrypt_data(data, key=None):
    """
    Decrypts the provided data using the encryption key and returns the decrypted data.
    If the key is not provided, it will be initialized from the environment.
    """
    if key is None:
        key = init()
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(data)
    return decrypted_data
