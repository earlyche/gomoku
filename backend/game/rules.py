import re
from typing import Union, TYPE_CHECKING

from singleton_decorator import singleton

from game.node import Node


if TYPE_CHECKING:
    from game.internal_types import TileXY


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

    def is_terminated(self, node: Node) -> Union[str, None]:
        if node.captures_x == 5:
            return node.player_1
        elif node.captures_o == 5:
            return node.player_2
        for line_key, line in node.lines.items():
            if self.X_WIN_TEMPLATE in line:
                return node.player_1
            elif self.O_WIN_TEMPLATE in line:
                return node.player_2
        return None

    @staticmethod
    def check_open_threes(node: Node, tile: 'TileXY') -> bool:
        child_node = node.create_child_with_new_tile(tile.to_tuple())

        if not child_node:
            return False
        return True


