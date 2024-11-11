import inspect
from functools import wraps

from .logger import scan_log


def logger(module_name):
    """
    Decorator for logging input data and method execution results.
    Logs successful execution and the output result, as well as errors if they occur.

    :param module_name: Module name to use in logs.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Logging arguments
            scan_log.debug_status_result(module_name, "INP", f"Calling async {func.__name__} with args: {args} kwargs: {kwargs}")
            try:
                # Calling the function
                result = await func(*args, **kwargs)
                # Logging the result
                scan_log.debug_status_result(module_name, "OUT", f"{func.__name__} returned {result}")
                return result
            except Exception as e:
                # Logging the error
                scan_log.debug_status_result(module_name, "ERR", f"Error in {func.__name__}: {e}")
                raise

        def sync_wrapper(*args, **kwargs):
            # Logging arguments
            scan_log.debug_status_result(module_name, "INP", f"Calling {func.__name__} with args: {args} kwargs: {kwargs}")
            try:
                # Calling the function
                result = func(*args, **kwargs)
                # Logging the result
                scan_log.debug_status_result(module_name, "OUT", f"{func.__name__} returned {result}")
                return result
            except Exception as e:
                # Logging the error
                scan_log.debug_status_result(module_name, "ERR", f"Error in {func.__name__}: {e}")
                raise

        # Determine if the function is asynchronous
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
    return decorator