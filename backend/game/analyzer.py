from singleton_decorator import singleton


@singleton
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

    def print_results(self):
        for variable in self.values:
            print(variable, self.values[variable])

    def update(self, variable, value):
        self.values[variable] += value

    def refresh(self):
        for variable in self.values:
            self.values[variable] = 0.0
