import time


def log(*values: object):
    print(values, time.strftime("%Y-%m-%d %H:%M:%S"))
