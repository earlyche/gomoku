import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, NamedTuple
from functools import wraps

from singleton_decorator import singleton

from game.analyzer import Analyzer

if TYPE_CHECKING:
    from game.node import Node


class Treat(NamedTuple):
    x_template: str
    o_template: str
    my_turn_value: int
    opponent_turn_value: int
    terminated: bool = False


class Heuristic(ABC):
    def __init__(self, *args, **kwargs):
        self.alpha_min: int = -1000000000000
        self.beta_max: int = 1000000000000
        super().__init__(*args, **kwargs)

    @abstractmethod
    def calculate(self, node: 'Node', *args, **kwargs) -> float:  # TODO: change float to int
        pass

    # TODO: add update_capture_value


def update_node_heuristic_value(func):
    @wraps(func)
    def wrapper(self, node: 'Node', *args, **kwargs):
        return_value = func(self, node, *args, **kwargs)
        node.heuristic_value = return_value
        return return_value

    return wrapper


@singleton
class HeuristicSimpleTreat(Heuristic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pattern_x = re.compile(f'(?=({"|".join([treat.x_template for treat in self.TREAT_TYPES])}))')
        self.pattern_o = re.compile(f'(?=({"|".join([treat.o_template for treat in self.TREAT_TYPES])}))')

        self.treats_x = {treat.x_template: (treat.my_turn_value, treat.opponent_turn_value)
                         for treat in self.TREAT_TYPES}

        self.treats_o = {treat.o_template: (treat.my_turn_value, treat.opponent_turn_value)
                         for treat in self.TREAT_TYPES}

    TREAT_TYPES = [
        Treat(x_template='xxxxx', o_template='ooooo', my_turn_value=1000000000, opponent_turn_value=1000000000, terminated=True),
        Treat(x_template='-xxxx-', o_template='-oooo-', my_turn_value=2000000, opponent_turn_value=1000000),
        Treat(x_template='-xxxx', o_template='-oooo', my_turn_value=2000000, opponent_turn_value=100000),
        Treat(x_template='xxxx-', o_template='oooo-', my_turn_value=2000000, opponent_turn_value=100000),
        Treat(x_template='xxx-x', o_template='ooo-o', my_turn_value=2000000, opponent_turn_value=100000),
        Treat(x_template='x-xxx', o_template='o-ooo', my_turn_value=2000000, opponent_turn_value=100000),
        Treat(x_template='xx-xx', o_template='oo-oo', my_turn_value=2000000, opponent_turn_value=100000),
        Treat(x_template='-xxx-', o_template='-ooo-', my_turn_value=200000, opponent_turn_value=10000),
        Treat(x_template='-xx-x-', o_template='-oo-o-', my_turn_value=7000, opponent_turn_value=1000),
        Treat(x_template='-x-xx-', o_template='-o-oo-', my_turn_value=7000, opponent_turn_value=1000),
        Treat(x_template='xxx-', o_template='ooo-', my_turn_value=6000, opponent_turn_value=2000),
        Treat(x_template='-xxx', o_template='-ooo', my_turn_value=6000, opponent_turn_value=2000),
        Treat(x_template='-x--xx-', o_template='-o--oo-', my_turn_value=5000, opponent_turn_value=100),
        Treat(x_template='-xx--x-', o_template='-oo--o-', my_turn_value=5000, opponent_turn_value=100),
    ]

    CAPTURE_VALUES = (
        10000,
        50000,
        100000,
        500000,
        1000000000,
    )

    @update_node_heuristic_value
    @Analyzer.update_time(Analyzer.HEURISTIC_CALCULATE)
    def calculate(self, node: 'Node', *args, **kwargs) -> float:
        score = 0
        maximizing_player = node.maximizing_player

        for line_key, line in node.lines.items():
            if len(line) < 4:
                continue

            o_treats = self.pattern_o.findall(line)
            x_treats = self.pattern_x.findall(line)

            if o_treats:
                for treat in o_treats:
                    treat_values = self.treats_o[treat]
                    if not maximizing_player:
                        score += treat_values[0] * (-1)

                    else:
                        score += treat_values[1] * (-1)

                    #  TODO: CHECK IF TERMINATED

            if x_treats:
                for treat in x_treats:
                    treat_values = self.treats_x[treat]
                    if maximizing_player:
                        score += treat_values[0]

                    else:
                        score += treat_values[1]

                    #  TODO: CHECK IF TERMINATED

        return score + node.capture_value

    @classmethod
    def update_capture_value(cls, node: 'Node') -> int:
        capture_count = node.captures_o if node.maximizing_player else node.captures_x
        index = capture_count if capture_count <= 4 else 4
        value = cls.CAPTURE_VALUES[index]
        node.capture_value += value * (-1) if node.maximizing_player else value
        return value
