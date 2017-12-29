from cryptography.fernet import Fernet

CRYPTO_KEY = Fernet.generate_key()

EMAIL_CONFIG = {
    'user': 'firstbestma@126.com',
    'password': 'Xiaoma_4693413',
    'mail_host': 'smtp.126.com',
}

DB_CONFIG = {
    'user': 'root',
    'password': None,
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'crossover',
}