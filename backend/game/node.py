from collections import defaultdict
from typing import Tuple, List, Dict, Set, Union, TYPE_CHECKING
from copy import deepcopy

from sortedcontainers import SortedList
from django.utils.functional import cached_property

from game.models import Tile
from game.internal_types import TileXY
from game.heuristics import HeuristicSimpleTreat


if TYPE_CHECKING:
    from game.models import Game


class Node:
    _x_size = 19
    _y_size = 19

    def __init__(
            self,
            player_1: str,
            player_2: str,
            maximizing_player: bool,
            tiles: Dict[str, List[Tuple[int, int]]],
            new_move: Tuple[int, int] = None,
            should_inspect: Set[Tuple[int, int]] = None,
            father: 'Node' = None,
            captures_x: int = None,
            captures_o: int = None,
    ):
        self.player_1 = player_1
        self.player_2 = player_2
        self.maximizing_player = maximizing_player
        self.tiles = tiles
        self.new_move = new_move
        self.should_inspect = should_inspect or self._get_inspections()
        self.father = father

        self._children: Dict[Tuple[int, int], Node] = {}
        self.heuristic_value = None
        self._sorted_tiles = None
        self.captures_x = captures_x if captures_x else 0
        self.captures_o = captures_o if captures_o else 0
        self.capture_value = father.capture_value if father else 0  # TODO: check
        self.chosen: Union[Tuple[Tuple[int, int], float], None] = None
        self._lines = None

    @property
    def children_amount(self) -> int:
        return len(self._children)

    @cached_property
    def player(self):
        return self.player_1 if self.maximizing_player else self.player_2

    @cached_property
    def another_player(self):
        return self.player_2 if self.maximizing_player else self.player_1

    @property
    def used_tiles(self) -> List[Tuple[int, int]]:
        return self.tiles[self.player_1] + self.tiles[self.player_2]

    @property
    def tiles_set(self) -> Set[Tuple[int, int]]:
        return set(self.used_tiles)

    @property
    def lines(self):  # TODO: maybe can be cached
        if not self._lines:
            self._find_lines()
        return self._lines

    @property
    def sorted_tiles(self) -> SortedList:
        if not self._sorted_tiles:
            self._sorted_tiles = SortedList()  # TODO: make tiles already sorted while creating and change sortedlist dinamically for created children
            self._sorted_tiles.update(self.tiles_set | self.should_inspect)
        return self._sorted_tiles

    def children(self):
        for coordinate in self.should_inspect:
            new_node = self.create_child_with_new_tile(coordinate)
            self._children[coordinate] = new_node  # TODO: Check if exists
            yield new_node

    def create_child_with_new_tile(self, tile: Tuple[int, int]):
        new_tiles = deepcopy(self.tiles)
        new_tiles[self.player].append(tile)

        inspections_for_tile = self._get_inspections_for_tile(tile)
        new_inspections = (self.should_inspect | inspections_for_tile) - {tile}
        node = Node(
            player_1=self.player_1,
            player_2=self.player_2,
            maximizing_player=not self.maximizing_player,
            tiles=new_tiles,
            should_inspect=new_inspections,
            new_move=tile,
            father=self,
        )
        captures = node.find_captures_to_delete(TileXY.from_tuple(node.new_move))
        if captures:
            node.update_from_captures(captures)

        return node

    def _find_lines(self):
        # TODO: add missing tiles between divided areas ??? or check that it isn't important
        self._lines = defaultdict(str)
        for tile in self.sorted_tiles:
            self.update_lines(tile)

    def update_lines(self, tile):  # TODO: add position
        """

        :param tile:

        1 - horizontal
        2 - vertical
        3 - diagonal (from up-left to down-right)
        4 - diagonal (from up-right to down-left)

        """
        if tile in self.tiles[self.player_1]:
            self._lines[(1, tile[1])] += 'x'
            self._lines[(2, tile[0])] += 'x'
            self._lines[(3, tile[0] - tile[1])] += 'x'
            self._lines[(4, tile[0] + tile[1])] += 'x'
        elif tile in self.tiles[self.player_2]:
            self._lines[(1, tile[1])] += 'o'
            self._lines[(2, tile[0])] += 'o'
            self._lines[(3, tile[0] - tile[1])] += 'o'
            self._lines[(4, tile[0] + tile[1])] += 'o'
        else:
            self._lines[(1, tile[1])] += '-'
            self._lines[(2, tile[0])] += '-'
            self._lines[(3, tile[0] - tile[1])] += '-'
            self._lines[(4, tile[0] + tile[1])] += '-'

    def _get_inspections(self) -> Set[Tuple[int, int]]:
        inspections = set()
        [inspections.update(self._get_inspections_for_tile(tile)) for tile in self.used_tiles]
        return inspections

    def _get_inspections_for_tile(self, tile: Tuple[int, int]) -> Set[Tuple[int, int]]:
        assert 0 <= tile[0] < self._x_size
        assert 0 <= tile[1] < self._y_size

        diff = 1  # TODO: check if it is optimal
        result_set = set()

        x_min = tile[0] - diff if tile[0] - diff >= 0 else 0
        x_max = tile[0] + diff if tile[0] + diff < self._x_size else self._x_size - 1
        y_min = tile[1] - diff if tile[1] - diff >= 0 else 0
        y_max = tile[1] + diff if tile[1] + diff < self._y_size else self._y_size - 1
        [
            result_set.add((i, j))
            for j in range(y_min, y_max + 1)
            for i in range(x_min, x_max + 1)
            if (i, j) not in self.tiles_set
        ]
        return result_set

    @cached_property
    def pretty(self):
        result = "  " + "".join(["{:2d}".format(index) for index in range(self._x_size)]) + "\n"
        for y in range(self._y_size):
            result += "{:2d} ".format(y)
            for x in range(self._x_size):
                if (x, y) in self.tiles[self.player_1]:
                    result += 'X '
                elif (x, y) in self.tiles[self.player_2]:
                    result += 'O '
                elif (x, y) in self.should_inspect:
                    result += '. '
                else:
                    result += '  '
            result += "\n"
        return result

    def print_children(self, tabs):
        print("\t" * tabs,
              self.new_move, "->",
              self.heuristic_value,
              self.capture_value,
              f"({self.maximizing_player})",
              f"CHOOSE: {self.chosen}" if self.chosen else "")

        for move, child in self._children.items():
            child.print_children(tabs + 1)

    @staticmethod
    def from_game(game: 'Game', player: str):
        data = {game.player_1: [], game.player_2: []}
        for tile in Tile.objects.filter(game=game):
            data[tile.player].append((tile.x_coordinate, tile.y_coordinate))

        return Node(
            player_1=game.player_1,
            player_2=game.player_2,
            maximizing_player=game.player_1 == player,
            tiles=data,
            captures_x=game.captures_x,
            captures_o=game.captures_o,
        )

    def find_captures_to_delete(self, tile_xy: TileXY) -> List[Tuple[TileXY, TileXY]]:
        captures = []
        template = 'xoox' if not self.maximizing_player else 'oxxo'
        lines = self.lines
        tiles = self.tiles

        if template in lines[(1, tile_xy.y)]:  # Horizontal
            if (tile_xy.x + 1, tile_xy.y) in tiles[self.player] \
                    and (tile_xy.x + 2, tile_xy.y) in tiles[self.player] \
                    and (tile_xy.x + 3, tile_xy.y) in tiles[self.another_player]:
                captures.append(
                    (TileXY(x=tile_xy.x + 1, y=tile_xy.y),
                     TileXY(x=tile_xy.x + 2, y=tile_xy.y),)
                )
            if (tile_xy.x - 1, tile_xy.y) in tiles[self.player] \
                    and (tile_xy.x - 2, tile_xy.y) in tiles[self.player] \
                    and (tile_xy.x - 3, tile_xy.y) in tiles[self.another_player]:
                captures.append(
                    (TileXY(x=tile_xy.x - 1, y=tile_xy.y),
                     TileXY(x=tile_xy.x - 2, y=tile_xy.y),)
                )

        if template in lines[(2, tile_xy.x)]:  # Vertical
            if (tile_xy.x, tile_xy.y + 1) in tiles[self.player] \
                    and (tile_xy.x, tile_xy.y + 2) in tiles[self.player] \
                    and (tile_xy.x, tile_xy.y + 3) in tiles[self.another_player]:
                captures.append(
                    (TileXY(x=tile_xy.x, y=tile_xy.y + 1),
                     TileXY(x=tile_xy.x, y=tile_xy.y + 2),)
                )
            if (tile_xy.x, tile_xy.y - 1) in tiles[self.player] \
                    and (tile_xy.x, tile_xy.y - 2) in tiles[self.player] \
                    and (tile_xy.x, tile_xy.y - 3) in tiles[self.another_player]:
                captures.append(
                    (TileXY(x=tile_xy.x, y=tile_xy.y - 1),
                     TileXY(x=tile_xy.x, y=tile_xy.y - 2),)
                )

        if template in lines[(3, tile_xy.x - tile_xy.y)]:  # Diagonal (from up-left to down-right)
            if (tile_xy.x + 1, tile_xy.y + 1) in tiles[self.player] \
                    and (tile_xy.x + 2, tile_xy.y + 2) in tiles[self.player] \
                    and (tile_xy.x + 3, tile_xy.y + 3) in tiles[self.another_player]:
                captures.append(
                    (TileXY(x=tile_xy.x + 1, y=tile_xy.y + 1),
                     TileXY(x=tile_xy.x + 2, y=tile_xy.y + 2),)
                )
            if (tile_xy.x - 1, tile_xy.y - 1) in tiles[self.player] \
                    and (tile_xy.x - 2, tile_xy.y - 2) in tiles[self.player] \
                    and (tile_xy.x - 3, tile_xy.y - 3) in tiles[self.another_player]:
                captures.append(
                    (TileXY(x=tile_xy.x - 1, y=tile_xy.y - 1),
                     TileXY(x=tile_xy.x - 2, y=tile_xy.y - 2),)
                )

        if template in lines[(4, tile_xy.x + tile_xy.y)]:  # Diagonal (from up-right to down-left)
            if (tile_xy.x + 1, tile_xy.y - 1) in tiles[self.player] \
                    and (tile_xy.x + 2, tile_xy.y - 2) in tiles[self.player] \
                    and (tile_xy.x + 3, tile_xy.y - 3) in tiles[self.another_player]:
                captures.append(
                    (TileXY(x=tile_xy.x + 1, y=tile_xy.y - 1),
                     TileXY(x=tile_xy.x + 2, y=tile_xy.y - 2),)
                )
            if (tile_xy.x - 1, tile_xy.y + 1) in tiles[self.player] \
                    and (tile_xy.x - 2, tile_xy.y + 2) in tiles[self.player] \
                    and (tile_xy.x - 3, tile_xy.y + 3) in tiles[self.another_player]:
                captures.append(
                    (TileXY(x=tile_xy.x - 1, y=tile_xy.y + 1),
                     TileXY(x=tile_xy.x - 2, y=tile_xy.y + 2),)
                )

        if self.maximizing_player:
            self.captures_x += len(captures)
        else:
            self.captures_o += len(captures)
        return captures

    def update_from_captures(self, captures: List[Tuple[TileXY, TileXY]]):
        for capture in captures:
            HeuristicSimpleTreat().update_capture_value(self)

            capture_0_tuple = capture[0].to_tuple()
            capture_1_tuple = capture[1].to_tuple()
            if self.maximizing_player:
                self.captures_o += 1
            else:
                self.captures_x += 1
            self.tiles[self.player].remove(capture_0_tuple)
            self.tiles[self.player].remove(capture_1_tuple)
            self.should_inspect.add(capture_0_tuple)
            self.should_inspect.add(capture_1_tuple)

    def __str__(self):
        return str(self.tiles)

    def __getitem__(self, tile):
        return self._children[tile]
