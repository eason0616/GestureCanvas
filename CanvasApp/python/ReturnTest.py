import time

ret = 0
while True:
    print(f"Now ret = {ret}", end='', flush=True)
    ret += 1
    time.sleep(1)