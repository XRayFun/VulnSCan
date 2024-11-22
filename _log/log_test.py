from _log import logger, LogLevel


@logger(module_name="test_module", log_level=LogLevel.INFO, filter_sensitive=True)
def some_method(user, password, other_param, data):
    return f"User {user} and password {password} processed with {other_param} and data {data}"


# Пример с вложенными коллекциями
if __name__ == "__main__":
    some_method("some_user", "some_password", 123, [{"user": "nested_user", "password": "nested_password"}])
