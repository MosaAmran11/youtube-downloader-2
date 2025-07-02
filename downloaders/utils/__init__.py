def raise_on_error():
    """
    Decorator to catch exceptions in a function and raise a new exception
    with the function name.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise Exception(f"[{func.__name__}] {type(e).__name__}: {e}") from e
        return wrapper
    return decorator
