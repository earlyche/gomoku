from time import time
from functools import wraps


class Analyzer:
    HEURISTIC_FIND_LINES = 'time_find_lines'
    HEURISTIC_CALCULATE = 'time_heuristic_calculate'
    ALL_TIME = 'all_time'
    NODE_COUNT = 'node_count'

    values = {
        HEURISTIC_FIND_LINES: 0.0,
        HEURISTIC_CALCULATE: 0.0,
        ALL_TIME: 0.0,
        NODE_COUNT: 0
    }

    @classmethod
    def print_results(cls):
        for variable in cls.values:
            print(variable, cls.values[variable])

    @classmethod
    def update_time(cls, time_variable):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time()
                return_value = func(*args, **kwargs)
                cls.values[time_variable] += time() - start_time
                return return_value
            return wrapper
        return decorator

    @classmethod
    def update(cls, variable, value):
        cls.values[variable] += value

    @classmethod
    def refresh(cls):
        for variable in cls.values:
            cls.values[variable] = 0.0

    @classmethod
    def get(cls, variable):
        return cls.values[variable]
