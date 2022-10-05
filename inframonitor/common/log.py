import sys
from datetime import datetime

from termcolor import colored


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_status(status):
    return colored('[ok]', 'green') if status else colored('[fail]', 'red')


def _current_time() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def log(*args, **kwargs):
    print(f'[LOG] {_current_time()} |', *args, **kwargs)


def dbg(*args, **kwargs):
    print(f'{bcolors.OKGREEN}[DBG] {_current_time()} |', *args, **kwargs, end=f"{bcolors.ENDC}\n")


def warn(*args, **kwargs):
    print(f'{bcolors.WARNING}[WARNING] {_current_time()} |', *args, **kwargs, end=f"{bcolors.ENDC}\n")


def err(*args, **kwargs):
    print(f'{bcolors.FAIL}[ERROR] {_current_time()} |', *args, file=sys.stderr, **kwargs, end=f"{bcolors.ENDC}\n")
