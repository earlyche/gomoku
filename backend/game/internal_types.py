from enum import Enum
from collections import namedtuple


class GameType(Enum):
    BOT = 'bot'
    MULTIPLAYER = 'multiplayer'


Treat = namedtuple('Treat', ['template', 'opponent_template', 'value'])


class TerminatedException(Exception):
    pass
