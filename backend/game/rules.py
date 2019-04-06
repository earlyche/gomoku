from typing import Union

from game.node import Node


class GameRules:
    X_WIN_TEMPLATE = 'xxxxx'
    O_WIN_TEMPLATE = 'ooooo'

    @classmethod
    def is_terminated(cls, node: Node) -> Union[str, None]:
        for line_key, line in node.lines.items():
            print(line)
            if cls.X_WIN_TEMPLATE in line:
                return node.player_1
            elif cls.O_WIN_TEMPLATE in line:
                return node.player_2
        return None
