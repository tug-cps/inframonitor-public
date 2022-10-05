from datetime import datetime

from common.log import log


def measure_time(func):
    def wrapper():
        start = datetime.now()
        func()
        end = datetime.now()
        log(f'Execution time: {(end - start).total_seconds()} seconds')

    return wrapper
