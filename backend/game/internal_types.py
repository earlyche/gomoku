from typing import NamedTuple, Tuple
from enum import Enum


class GameType(Enum):
    BOT = 'bot'
    MULTIPLAYER = 'multiplayer'


class Capture(NamedTuple):
    symbol: str = None
    tile: Tuple[int, int] = None


class TerminatedException(Exception):
    pass
