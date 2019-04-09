from typing import NamedTuple, Tuple
from enum import Enum


class GameType(Enum):
    BOT = 'bot'
    MULTIPLAYER = 'multiplayer'


class TileXY(NamedTuple):
    x: int
    y: int

    @staticmethod
    def from_serializer(tile_serializer):
        return TileXY(
            x=tile_serializer.x_coordinate,
            y=tile_serializer.y_coordinate,
        )


class TerminatedException(Exception):
    pass
