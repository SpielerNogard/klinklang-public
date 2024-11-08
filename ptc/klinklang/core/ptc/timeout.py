import signal


def timeout(seconds):
    """Decorator to add a timeout to a function."""

    def process_timeout(func):
        def handle_timeout(signum, frame):
            raise TimeoutError("The function timed out")

        def wrapper(*args, **kwargs):
            if not hasattr(signal, "SIGALRM"):
                return func(*args, **kwargs)

            signal.signal(signal.SIGALRM, handle_timeout)
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)  # No need to time out!
            return result

        return wrapper

    return process_timeout
