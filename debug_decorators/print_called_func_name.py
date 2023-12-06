def print_func_calls(cls):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(func.__name__)
            return func(*args, **kwargs)
        return wrapper
    for attr in cls.__dict__:
        if callable(getattr(cls, attr)):
            setattr(cls, attr, decorator(getattr(cls, attr)))
    return cls
