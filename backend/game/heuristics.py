from abc import ABC, abstractmethod
from collections import namedtuple
from typing import TYPE_CHECKING

from game.analyzer import Analyzer

if TYPE_CHECKING:
    from game.node import Node


Treat = namedtuple('Treat', ['x_template', 'o_template', 'my_turn_value', 'opponent_turn_value'])


class Heuristic(ABC):
    def __init__(self, *args, **kwargs):
        self.alpha_min: int = -1000000000000
        self.beta_max: int = 1000000000000
        super().__init__(*args, **kwargs)

    @abstractmethod
    def calculate(self, node: 'Node', *args, **kwargs) -> float:  #TODO: change float to int
        pass


class HeuristicSimpleTreat(Heuristic):
    TREAT_TYPES = [  # These types should be in descending order by 'value'
        # Treat(x_template='xxxxx', o_template='ooooo', my_turn_value=1000000000, opponent_turn_value=1000000000),
        Treat(x_template='-xxxx-', o_template='-oooo-', my_turn_value=1000000, opponent_turn_value=1000000),
        Treat(x_template='-xxxx', o_template='-oooo', my_turn_value=1000000, opponent_turn_value=100000),
        Treat(x_template='xxx-x', o_template='ooo-o', my_turn_value=1000000, opponent_turn_value=100000),
        Treat(x_template='xx-xx', o_template='oo-oo', my_turn_value=1000000, opponent_turn_value=100000),
        Treat(x_template='-xxx-', o_template='-ooo-', my_turn_value=100000, opponent_turn_value=10000),
        Treat(x_template='-xx-x-', o_template='-oo-o-', my_turn_value=7000, opponent_turn_value=1000),
        Treat(x_template='xxx-', o_template='ooo-', my_turn_value=6000, opponent_turn_value=2000),
        Treat(x_template='-x--xx-', o_template='-o--oo-', my_turn_value=5000, opponent_turn_value=100),
    ]

    X_WIN_TEMPLATE = 'xxxxx'
    O_WIN_TEMPLATE = 'ooooo'

    @Analyzer.update_time(Analyzer.HEURISTIC_CALCULATE)
    def calculate(self, node: 'Node', *args, **kwargs) -> float:
        score = 0
        maximizing_player = node.maximizing_player
        for line_key, line in node.lines.items():
            for treat in self.TREAT_TYPES:
                if treat.x_template in line or treat.x_template[::-1] in line:
                    if maximizing_player:
                        score += treat.my_turn_value
                    else:
                        score += treat.opponent_turn_value
                if treat.o_template in line or treat.o_template[::-1] in line:
                    if not maximizing_player:
                        score += treat.my_turn_value * (-1)
                    else:
                        score += treat.opponent_turn_value * (-1)
        return score
