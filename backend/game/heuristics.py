from abc import ABC, abstractmethod
from collections import namedtuple
from typing import TYPE_CHECKING

from django.utils.functional import cached_property

from game.analyzer import Analyzer

if TYPE_CHECKING:
    from game.node import Node


Treat = namedtuple('Treat', ['template', 'opponent_template', 'value'])


class Heuristic(ABC):
    def __init__(self, *args, **kwargs):
        self.alpha_min: float = -9999.0
        self.beta_max: float = 9999.0
        super().__init__(*args, **kwargs)

    @abstractmethod
    def calculate(self, node: 'Node', *args, **kwargs) -> float:
        pass


class HeuristicSimpleTreat(Heuristic):
    TREAT_TYPES = [  # These types should be in descending order by 'value'
        Treat(template='xxxxx', opponent_template='ooooo', value=100),
        Treat(template='-xxxx-', opponent_template='-oooo-', value=60),
        Treat(template='-xxxx', opponent_template='-oooo', value=40),
        Treat(template='xxx-x', opponent_template='ooo-o', value=40),
        Treat(template='xx-xx', opponent_template='oo-oo', value=40),
        Treat(template='-xxx-', opponent_template='-ooo-', value=30),
        Treat(template='-x--xx-', opponent_template='-o--oo-', value=20),
        Treat(template='xxx--', opponent_template='ooo--', value=20),
        Treat(template='-xx-x-', opponent_template='-oo-o-', value=10),
    ]

    @Analyzer.update_time(Analyzer.HEURISTIC_CALCULATE)
    def calculate(self, node: 'Node', *args, **kwargs) -> float:  # TODO: refactor
        max_value = 0
        min_value = 0
        for line_key, line in node.lines.items():
            for treat in self.TREAT_TYPES:
                if treat.value <= max_value and treat.value * (-1) >= min_value:
                    break
                if treat.template in line or treat.template[::-1] in line:
                    max_value = treat.value
                if treat.opponent_template in line or treat.opponent_template[::-1] in line:
                    min_value = treat.value * (-1)
                    # break
            if max_value == self.terminated_value or min_value * (-1) == self.terminated_value:
                break

        node.heuristic_value = max_value if max_value > min_value * (-1) else min_value
        # if node.heuristic_value:
        #     print(node.heuristic_value, node.father.new_move, node.new_move, node.maximizing_player)
        #     print(node.pretty)

        return node.heuristic_value

    @cached_property
    def terminated_value(self):
        return self.TREAT_TYPES[0].value


if __name__ == '__main__':
    pass
