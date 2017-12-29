# This is a client script.

import psutil
import time
import json
import os
import platform

from cryptography.fernet import Fernet


CRYPTO_KEY = b'mWK49Y-bLpaycw7xXaTO_IoFs_8vBeQtSepE0qbIva8='

def collect_metrix():
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    mem_percent = (mem.available / mem.total) * 100
    uptime = int(time.time()) - psutil.boot_time()
    log_content = open('SysInfo/get_windows_events.html').read()

    result = {
        'mem_percent': mem_percent,
        'cpu_percent': cpu_percent,
        'uptime': uptime,
        'log_content': log_content,
    }
    return json.dumps(result)


def crypto_string(key, content):
    cipher_suite = Fernet(key)
    cipher_text = cipher_suite.encrypt(content.encode('utf-8'))
    return cipher_text


if __name__ == '__main__':
    content = collect_metrix()
    cipher_text = crypto_string(CRYPTO_KEY, content)
    print(cipher_text.decode())