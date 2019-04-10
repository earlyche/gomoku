from typing import Union

from singleton_decorator import singleton

from game.node import Node


@singleton
class GameRules:
    X_WIN_TEMPLATE = 'xxxxx'
    O_WIN_TEMPLATE = 'ooooo'

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
