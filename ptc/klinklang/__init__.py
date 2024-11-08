__version__ = "0.0.1"

import datetime


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Logger:
    @staticmethod
    def now() -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    @staticmethod
    def info(message):
        print(f"{bcolors.OKGREEN}[INFO][{Logger.now()}] {message}")

    @staticmethod
    def info_cyan(message):
        print(f"{bcolors.OKCYAN}[INFO][{Logger.now()}] {message}")

    @staticmethod
    def warning(message):
        print(f"{bcolors.WARNING}[WARNING][{Logger.now()}] {message}")

    @staticmethod
    def error(message):
        print(f"{bcolors.FAIL}[ERROR][{Logger.now()}] {message}")


logger = Logger
