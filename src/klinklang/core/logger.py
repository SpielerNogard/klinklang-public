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
    def __init__(self, name: str = None):
        self._name = name

    @staticmethod
    def now() -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    @property
    def _prefix(self):
        prefix = ""
        if self._name:
            prefix = f"[{self._name}]"
        return f"{prefix}[{Logger.now()}]"

    def info(self, message):
        print(f"{bcolors.OKGREEN}[INFO][{self._prefix}] {message}")

    def info_cyan(self, message):
        print(f"{bcolors.OKCYAN}[INFO][{self._prefix}] {message}")

    def warning(self, message):
        print(f"{bcolors.WARNING}[WARNING][{self._prefix}] {message}")

    def error(self, message):
        print(f"{bcolors.FAIL}[ERROR][{self._prefix}] {message}")
