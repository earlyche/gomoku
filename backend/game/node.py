import time
from collections import defaultdict
from typing import Tuple, List, Dict, Set
from copy import deepcopy

from sortedcontainers import SortedList
from django.utils.functional import cached_property

from game.time_analyzer import TimeAnalyzer


time_analyzer = TimeAnalyzer()
print(time_analyzer)


class Node:
    def __init__(
            self,
            player_1: str,
            player_2: str,
            maximizing_player: bool,
            tiles: Dict[str, List[Tuple[int, int]]],
            should_inspect: Set[Tuple[int, int]] = None,
            lines: Dict[Tuple[int, int], str] = None,
            new_move: Tuple[int, int] = None,
            father: 'Node' = None,
            sorted_tiles: 'SortedList' = None,
    ):
        self._x_size = 19
        self._y_size = 19
        self._sorted_tiles = sorted_tiles
        self.player_1 = player_1
        self.player_2 = player_2
        self.maximizing_player = maximizing_player
        self.tiles = tiles
        self.new_move = new_move
        self.should_inspect = should_inspect or self._get_inspections()
        self._lines = lines
        self._children: Dict[Tuple[int, int], Node] = {}
        self.father = father
        self.heuristic_value = None

        self.chosen: Tuple[Tuple[int, int], float] = None

    @property
    def children_amount(self) -> int:
        return len(self._children)

    @cached_property
    def player(self):
        return self.player_1 if self.maximizing_player else self.player_2

    @cached_property
    def another_player(self):
        return self.player_2 if self.maximizing_player else self.player_1

    @cached_property
    def used_tiles(self) -> List[Tuple[int, int]]:
        return self.tiles[self.player_1] + self.tiles[self.player_2]

    @cached_property
    def tiles_set(self) -> Set[Tuple[int, int]]:
        return set(self.used_tiles)

    @property
    def lines(self):
        if not self._lines:
            self._find_lines()
        return self._lines

    @property
    def sorted_tiles(self) -> SortedList:
        if not self._sorted_tiles:
            self._sorted_tiles = SortedList()  # TODO: make tiles already sorted while creating and change sortedlist dinamically for created children
            self._sorted_tiles.update(self.tiles_set | self.should_inspect)
            # print("SORTED")
        return self._sorted_tiles
        # return tiles

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
        # new_sorted_tiles = deepcopy(self.sorted_tiles)
        # new_sorted_tiles.update(inspections_for_tile - self.tiles_set)
        node = Node(
            player_1=self.player_1,
            player_2=self.player_2,
            maximizing_player=not self.maximizing_player,
            tiles=new_tiles,
            should_inspect=new_inspections,
            new_move=tile,
            father=self,
            # sorted_tiles=new_sorted_tiles,
            # lines=self.lines,
        )

        # TODO: BAD IDEA, because of order and sign('x' or 'o'), Should place element in correct position
        # node.oposite_update_lines(tile)
        return node

    def _find_lines(self):

        time1 = time.time()

        # TODO: add missing tiles between divided areas ??? maybe it's not important

        self._lines = defaultdict(str)
        for tile in self.sorted_tiles:
            self.update_lines(tile)

        time_analyzer.update(time_analyzer.HEURISTIC_FIND_LINES, time.time() - time1)

    def update_lines(self, tile):  # TODO: add position
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

        diff = 2  # TODO: check if it is optimal
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
              f"({self.maximizing_player})",
              f"CHOOSE: {self.chosen}" if self.chosen else "")

        for move, child in self._children.items():
            child.print_children(tabs + 1)

    def __str__(self):
        return str(self.tiles)

    def __getitem__(self, tile):
        return self._children[tile]
