import re
from typing import Union, TYPE_CHECKING

from singleton_decorator import singleton

from game.node import Node


if TYPE_CHECKING:
    from game.internal_types import TileXY


DRAW = "Draw"


@singleton
class GameRules:
    X_WIN_TEMPLATE = 'xxxxx'
    O_WIN_TEMPLATE = 'ooooo'

    o_open_threes = (
        '-ooo-',
        '-o-oo-',
        '-oo-o-',
    )

    x_open_threes = (
        '-xxx-',
        '-x-xx-',
        '-xx-x-',
    )

    def __init__(self):
        self.pattern_x = re.compile(f'(?=({"|".join([treat for treat in self.x_open_threes])}))')
        self.pattern_o = re.compile(f'(?=({"|".join([treat for treat in self.o_open_threes])}))')

    @staticmethod
    def _win_by_captures(node):
        if node.captures_x == 5:
            return node.player_1
        elif node.captures_o == 5:
            return node.player_2
        else:
            return None

    def is_terminated(self, node: Node) -> Union[str, None]:
        win_by_captures = self._win_by_captures(node)
        if win_by_captures:
            return win_by_captures

        winners = set()
        for line_key, line in node.lines.items():
            if self.X_WIN_TEMPLATE in line:
                winners.add(node.player_1)
            if self.O_WIN_TEMPLATE in line:
                winners.add(node.player_2)

        if len(winners) == 1:
            return list(winners)[0]
        elif len(winners) > 1:
            print(winners)
            return DRAW
        else:
            return None

    def deeper_winner_check(self, node: Node):
        supposed_winner = self.is_terminated(node)
        if not supposed_winner:
            return supposed_winner

        win_by_captures = self._win_by_captures(node)
        if win_by_captures:
            return win_by_captures

        for child in node.children():
            winner_check = self.is_terminated(child)
            if winner_check != supposed_winner and winner_check != DRAW:
                return winner_check
        return supposed_winner

    @staticmethod
    def check_open_threes(node: Node, tile: 'TileXY') -> bool:
        child_node = node.create_child_with_new_tile(tile.to_tuple())

        if not child_node:
            return False
        return True


