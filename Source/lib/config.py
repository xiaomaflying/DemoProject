from cryptography.fernet import Fernet

CRYPTO_KEY = Fernet.generate_key()

EMAIL_CONFIG = {
    'user': 'firstbestma@126.com',
    'password': 'Xiaoma_4693413',
    'mail_host': 'smtp.126.com',
}
