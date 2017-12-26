# This is a client script.

import psutil
import time
import json
import os
import platform

from cryptography.fernet import Fernet


CRYPTO_KEY = b'mWK49Y-bLpaycw7xXaTO_IoFs_8vBeQtSepE0qbIva8='


def get_secure_log_platform():
    sys_version = platform.system()
    if sys_version in ('linux', 'Darwin'):
        if os.path.exists('/var/log/auth.log'):
            with open('/var/log/auth.log') as f:
                content = f.read()
            return content
    elif sys_version == 'Windows':
        # TODO: Not support windows system
        return
    return


def collect_metrix():
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    mem_percent = mem.available / mem.total
    uptime = int(time.time()) - psutil.boot_time()
    log_content = get_secure_log_platform()

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
    # plain_text = Fernet(CRYPTO_KEY).decrypt(cipher_text)