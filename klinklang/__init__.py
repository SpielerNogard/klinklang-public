__version__ = "0.0.1"


class Logger:
    @staticmethod
    def info(message):
        print(f"[INFO][KLINKLANG]: {message}")

    @staticmethod
    def warning(message):
        print(f"[WARNING][KLINKLANG]: {message}")

    @staticmethod
    def error(message):
        print(f"[ERROR][KLINKLANG]: {message}")


logger = Logger
