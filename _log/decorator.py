import inspect
from functools import wraps

from .logger import vsc_log, LogLevel


def logger(module_name:str, log_level:LogLevel=None):
    """
    Decorator for logging input data and method execution results.
    Logs successful execution and the output result, as well as errors if they occur.

    :param module_name: Module name to use in logs.
    :param log_level: Level of auto-logging
    """
    if log_level is None:
        log_level = LogLevel.DEBUG

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Logging arguments
            vsc_log.log_result(log_level, module_name, "INP", f"Calling async {func.__name__} with args: {args} kwargs: {kwargs}")
            try:
                # Calling the function
                result = await func(*args, **kwargs)
                # Logging the result
                vsc_log.log_result(log_level, module_name, "OUT", f"Async {func.__name__} returned {result}")
                return result
            except Exception as e:
                # Logging the error
                vsc_log.log_result(log_level, module_name, "ERR", f"Error in async {func.__name__}: {e}")
                raise

        def sync_wrapper(*args, **kwargs):
            # Logging arguments
            vsc_log.log_result(log_level, module_name, "INP", f"Calling async {func.__name__} with args: {args} kwargs: {kwargs}")
            try:
                # Calling the function
                result = func(*args, **kwargs)
                # Logging the result
                vsc_log.log_result(log_level, module_name, "OUT", f"Async {func.__name__} returned {result}")
                return result
            except Exception as e:
                # Logging the error
                vsc_log.log_result(log_level, module_name, "ERR", f"Error in async {func.__name__}: {e}")
                raise

        # Determine if the function is asynchronous
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
    return decorator