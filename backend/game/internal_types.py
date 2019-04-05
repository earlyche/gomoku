from enum import Enum


class GameType(Enum):
    BOT = 'bot'
    MULTIPLAYER = 'multiplayer'


class TerminatedException(Exception):
    pass
