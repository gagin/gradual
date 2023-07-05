import argparse
import sys
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
    return parser.parse_args()

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
    else:
        key = init()

    if args.encrypt:
        encrypt_file(args.encrypt, key)

    if args.decrypt:
        decrypt_file(args.decrypt, key)

if __name__ == "__main__":
    main()
