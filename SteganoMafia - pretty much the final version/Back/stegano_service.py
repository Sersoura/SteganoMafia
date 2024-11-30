from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from secrets import token_bytes
from stegano import lsb

def generate_key(encryption_type):
    if encryption_type == "AES-128":
        return token_bytes(16)
    elif encryption_type == "AES-192":
        return token_bytes(24)
    elif encryption_type == "AES-256":
        return token_bytes(32)
    else:
        raise ValueError("Type de chiffrement non valide.")

def encrypt_message(message, key):
    iv = token_bytes(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_message = padder.update(message.encode()) + padder.finalize()

    encrypted_message = iv + encryptor.update(padded_message) + encryptor.finalize()
    return encrypted_message

def decrypt_message(encrypted_message, key):
    iv = encrypted_message[:16]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    padded_message = decryptor.update(encrypted_message[16:]) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    message = unpadder.update(padded_message) + unpadder.finalize()

    return message.decode()

def encode_message(image_path, message):
    encoded_image_path = f"{image_path}_encoded.png"
    lsb.hide(image_path, message.hex()).save(encoded_image_path)
    return encoded_image_path

def decode_message(image_path):
    return bytes.fromhex(lsb.reveal(image_path))
