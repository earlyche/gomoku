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

    @staticmethod
    def from_dict(data: dict):
        return TileXY(
            x=data['x_coordinate'],
            y=data['y_coordinate'],
        )

    @staticmethod
    def from_tuple(coordinates_tuple: Tuple[int, int]):
        return TileXY(
            x=coordinates_tuple[0],
            y=coordinates_tuple[1],
        )

    def to_tuple(self):
        return self.x, self.y


class TerminatedException(Exception):
    pass
