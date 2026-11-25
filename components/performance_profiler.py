import time
from functools import wraps


def profile_function(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        start_time = time.perf_counter()

        try:
            return function(*args, **kwargs)

        finally:
            elapsed = time.perf_counter() - start_time

            print(
                f"[PERFORMANCE] "
                f"{function.__name__}: "
                f"{elapsed * 1000:.2f} ms"
            )

    return wrapper