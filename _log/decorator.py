import inspect
from functools import wraps
from typing import Any

from _conf import SENSITIVE_KEYS
from .logger import vsc_log, LogLevel


def logger(module_name:str = None, log_level:LogLevel = None, filter_sensitive:bool = True):
    """
    Decorator for logging input data and method execution results.
    Logs successful execution and the output result, as well as errors if they occur.

    :param module_name: Module name to use in logs.
    :param log_level: Level of auto-logging
    :param filter_sensitive: Specifies whether arguments should be filtered for sensitive information for logging purposes
    """
    module = f"auto.{module_name}" if module_name else "auto"
    level = log_level if log_level else LogLevel.DEFAULT_AUTOLOG_LEVEL

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            f_args, f_kwargs = _filter_args(args, kwargs) if filter_sensitive else args, kwargs
            # Logging arguments
            vsc_log.log_result(level=level, module=module, status="INP", result=f"Calling async {func.__name__} with args: {f_args} kwargs: {f_kwargs}")
            try:
                # Calling the function
                result = await func(*args, **kwargs)
                # Logging the result
                vsc_log.log_result(level=level, module=module, status="OUT", result=f"Async {func.__name__} returned {result}")
                return result
            except Exception as e:
                # Logging the error
                vsc_log.log_result(level=level, module=module, status="ERR", result=f"Error in async {func.__name__}: {e}")
                raise

        def sync_wrapper(*args, **kwargs):
            f_args, f_kwargs = _filter_args(args, kwargs) if filter_sensitive else args, kwargs
            # Logging arguments
            vsc_log.log_result(level=level, module=module, status="INP", result=f"Calling sync {func.__name__} with args: {f_args} kwargs: {f_kwargs}")
            try:
                # Calling the function
                result = func(*args, **kwargs)
                # Logging the result
                vsc_log.log_result(level=level, module=module, status="OUT", result=f"Sync {func.__name__} returned {result}")
                return result
            except Exception as e:
                # Logging the error
                vsc_log.log_result(level=level, module=module, status="ERR", result=f"Error in sync {func.__name__}: {e}")
                raise

        # Determine if the function is asynchronous
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
    return decorator


def _filter_args(args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[tuple[Any, ...], dict[str, Any]]:
    """
    Фильтрует значения в переданных аргументах, заменяя их на '*****' для защищённых ключей.
    :param args: Кортеж позиционных аргументов
    :param kwargs: Словарь именованных аргументов
    :return: Кортеж с отфильтрованными позиционными и именованными аргументами
    """

    def filter_value(value: Any) -> Any:
        """
        Рекурсивная функция для фильтрации значений в коллекциях (списки, словари).
        :param value: Значение для фильтрации
        :return: Отфильтрованное значение
        """
        if isinstance(value, dict):
            # Для словаря: если ключ в SENSITIVE_KEYS, фильтруем его значение
            return {key: '*****' if key in SENSITIVE_KEYS else filter_value(val) for key, val in value.items()}
        elif isinstance(value, list):
            # Для списка: рекурсивно фильтруем каждый элемент списка
            return [filter_value(item) for item in value]
        elif isinstance(value, str):
            # Если это строка, проверяем её на наличие секретных ключей
            return '*****' if any(key in value.lower() for key in SENSITIVE_KEYS) else value
        else:
            # Если это не строка, не список и не словарь, возвращаем как есть
            return value

    # Фильтрация позиционных аргументов
    filtered_args = tuple(filter_value(arg) for arg in args)

    # Фильтрация именованных аргументов
    filtered_kwargs = {key: filter_value(value) for key, value in kwargs.items()}

    return filtered_args, filtered_kwargs
