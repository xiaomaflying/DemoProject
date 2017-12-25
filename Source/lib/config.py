from cryptography.fernet import Fernet

CRYPTO_KEY = Fernet.generate_key()
