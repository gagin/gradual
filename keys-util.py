import argparse
import sys
import os
from keys_lib import init, encrypt_data, decrypt_data

def parse_arguments():
    """
    Parses the command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Encryption utility using environment key")
    parser.add_argument("-askforkey", action="store_true", help="Prompt for encryption key")
    parser.add_argument("-encrypt", metavar="FILE", help="Encrypt the specified file")
    parser.add_argument("-decrypt", metavar="FILE", help="Decrypt the specified file")
    parser.add_argument("-key", help="Encryption key")
    parser.add_argument("-showkey", action="store_true", help="Print the export command to initialize the environment variable with the encryption key")
    parser.add_argument("-newkey", action="store_true", help="Generate a new encryption key and print the export command to initialize the environment variable with the new key")
    return parser.parse_args()

def generate_new_key():
    """
    Generates a new encryption key and prints the export command to initialize the environment variable with the new key.
    """
    os.environ.pop("PY_ENCRYPTION_KEY", None)
    key = init(new="yes")
    key_str = key.decode("utf-8")
    command = f'export PY_ENCRYPTION_KEY="{key_str}"'
    print(command)


def show_key():
    """
    Prints the export command to initialize the environment variable with the encryption key.
    """
    key = init()
    key_str = key.decode("utf-8")
    command = f'export PY_ENCRYPTION_KEY="{key_str}"'
    print(command)

def prompt_for_key():
    """
    Prompts the user to enter the encryption key.
    """
    key = input("Enter the encryption key: ")
    return key.encode("utf-8")

def encrypt_file(file_path, key):
    """
    Encrypts the specified file using the given key and prints the encrypted data.
    """
    with open(file_path, "rb") as file:
        plaintext = file.read()
    encrypted_data = encrypt_data(plaintext, key)
    sys.stdout.buffer.write(encrypted_data)

def decrypt_file(file_path, key):
    """
    Decrypts the specified file using the given key and prints the decrypted data.
    """
    with open(file_path, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = decrypt_data(encrypted_data, key)
    sys.stdout.buffer.write(decrypted_data)

def main():
    """
    Main function to handle the command-line arguments and perform the requested operations.
    """
    args = parse_arguments()

    key = None
    if args.askforkey:
        key = prompt_for_key()
    elif args.key:
        key = args.key.encode("utf-8")
    elif args.showkey:
        show_key()
        return
    elif args.newkey:
        generate_new_key()
        return
    else:
        key = init()

    if args.encrypt:
        encrypt_file(args.encrypt, key)

    if args.decrypt:
        decrypt_file(args.decrypt, key)


if __name__ == "__main__":
    main()
