# This is a client script.

import psutil

cpu_percent = psutil.cpu_percent(interval=1)
print(cpu_percent)

mem = psutil.virtual_memory()
print(mem)

mem_percent = mem.available / mem.total
print(mem_percent)