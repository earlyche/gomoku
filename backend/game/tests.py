from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from game.internal_types import GameType
from game.models import Game, Tile
from game.algorithm import Minimax
from game.node import Node
from game.rules import GameRules
from game.heuristics import Heuristic, HeuristicSimpleTreat


class GameApiTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_create_game_success(self):
        old_amount_of_games = Game.objects.count()
        request_body = {
            'type': GameType.BOT.value,
            'player_1': 'player_1',
            'player_2': 'player_2'
        }
        response = self.client.post(
            reverse('game'),
            request_body
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_amount_of_games = Game.objects.count()
        self.assertEqual(old_amount_of_games + 1, new_amount_of_games)

    def test_create_game_fail(self):
        old_amount_of_games = Game.objects.count()
        request_body_not_existed_type = {
            'type': "dummy",
            'player_1': 'player_1',
            'player_2': 'player_2'
        }
        request_body_same_players = {
            'type': GameType.BOT.value,
            'player_1': 'player_1',
            'player_2': 'player_1'
        }

        response = self.client.post(
            reverse('game'),
            request_body_not_existed_type
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            reverse('game'),
            request_body_same_players
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        new_amount_of_games = Game.objects.count()
        self.assertEqual(old_amount_of_games, new_amount_of_games)

    def test_create_tile_success(self):
        game = Game.objects.create(type=GameType.BOT.value, player_1="player_1", player_2="player_2")
        old_amount_of_tiles = Tile.objects.count()
        request_body = {
            'x_coordinate': 1,
            'y_coordinate': 6,
            'game_id': game.id,
            'player': 'player_2'
        }
        response = self.client.post(
            reverse('tile'),
            request_body
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_amount_of_tiles = Tile.objects.count()
        self.assertEqual(old_amount_of_tiles + 1, new_amount_of_tiles)

    def test_create_tile_fail(self):
        game = Game.objects.create(type=GameType.BOT.value, player_1="player_1", player_2="player_2")
        old_amount_of_tiles = Tile.objects.count()
        request_body_coordinate_less_zero = {
            'x_coordinate': -1,
            'y_coordinate': 6,
            'game_id': game.id,
            'player': 'player_2'
        }
        request_body_coordinate_bigger_18 = {
            'x_coordinate': 1,
            'y_coordinate': 19,
            'game_id': game.id,
            'player': 'player_2'
        }
        request_body_game_not_existed = {
            'x_coordinate': 1,
            'y_coordinate': 1,
            'game_id': 999,
            'player': 'player_2'
        }
        request_body_incorrect_player = {
            'x_coordinate': 1,
            'y_coordinate': 1,
            'game_id': game.id,
            'player': 'not_existed_player'
        }

        response = self.client.post(
            reverse('tile'),
            request_body_coordinate_less_zero
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            reverse('tile'),
            request_body_coordinate_bigger_18
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            reverse('tile'),
            request_body_game_not_existed
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            reverse('tile'),
            request_body_incorrect_player
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        new_amount_of_tiles = Tile.objects.count()
        self.assertEqual(old_amount_of_tiles, new_amount_of_tiles)

    def test_unique_tile(self):
        game = Game.objects.create(type=GameType.BOT.value, player_1="player_1", player_2="player_2")
        old_amount_of_tiles = Tile.objects.count()
        request_body = {
            'x_coordinate': 1,
            'y_coordinate': 6,
            'game_id': game.id,
            'player': 'player_2'
        }
        response = self.client.post(
            reverse('tile'),
            request_body
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        request_body = {
            'x_coordinate': 1,
            'y_coordinate': 6,
            'game_id': game.id,
            'player': 'player_1'
        }
        response = self.client.post(
            reverse('tile'),
            request_body
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        new_amount_of_tiles = Tile.objects.count()
        self.assertEqual(old_amount_of_tiles + 1, new_amount_of_tiles)


class GameTestCase(TestCase):
    @classmethod
    def setUpClass(cls):

        class HeuristicDummy(Heuristic):
            def calculate(self, node: Node, *args, **kwargs):
                return 1.0

        class HeuristicDummyZero(Heuristic):
            def __init__(self):
                super().__init__()
                self.alpha_min = 0.0
                self.beta_max = 0.0

            def calculate(self, node: Node, *args, **kwargs):
                return -1.0

        super().setUpClass()
        cls.heuristic_dummy = HeuristicDummy()
        cls.heuristic_dummy_zero = HeuristicDummyZero()
        cls.heuristic_simple_treat = HeuristicSimpleTreat()

    def test_simple_minimax_validation(self):
        start_node = Node(player_1='dummy', player_2='dummy2', maximizing_player=True, tiles={'dummy': [(1, 1)], 'dummy2': []})
        minimax = Minimax(self.heuristic_dummy, GameRules())
        minimax_zero = Minimax(self.heuristic_dummy_zero, GameRules())

        with self.subTest('infinities'):
            minimax_value = minimax.calculate_minimax(node=start_node, depth=3)[0]
            self.assertEqual(1.0, minimax_value)

        with self.subTest('zeros'):
            minimax_value = minimax.calculate_minimax(node=start_node, alpha=0.0, beta=0.0, depth=3)[0]
            self.assertEqual(0.0, minimax_value)

        with self.subTest('infinities_with_minus'):
            minimax_value = minimax_zero.calculate_minimax(node=start_node, depth=3)[0]
            self.assertEqual(0.0, minimax_value)

        with self.subTest('zeros_with_minus'):
            minimax_value = minimax_zero.calculate_minimax(node=start_node, alpha=-10.0, beta=10.0, depth=3)[0]
            self.assertEqual(-1.0, minimax_value)

    def test_node_should_inspect_set(self):
        data = {'p1': [(9, 9), (10, 9), (12, 12)], 'p2': [(10, 10), (11, 10), (11, 11)]}
        node = Node(
            player_1='p1',
            player_2='p2',
            maximizing_player=True,
            tiles=data,
        )
        should_inspect = {
            (10, 11), (13, 13), (9, 8), (7, 7), (14, 13), (8, 9), (11, 14), (13, 8), (7, 11), (12, 9), (10, 8),
            (13, 12), (10, 7), (12, 13), (8, 10), (10, 12), (9, 11), (7, 10), (14, 14), (12, 10), (9, 7), (11, 13),
            (13, 11), (14, 10), (12, 14), (8, 11), (11, 9), (12, 7), (10, 13), (9, 10), (8, 7), (12, 11), (11, 12),
            (13, 10), (7, 9), (14, 11), (11, 7), (9, 13), (8, 12), (11, 8), (13, 14), (14, 12), (8, 8), (10, 14),
            (13, 9), (7, 8), (9, 12), (12, 8)
        }
        self.assertEqual(
            should_inspect,
            node.should_inspect
        )

        with self.subTest('create child'):
            child_node = node.create_child_with_new_tile((6, 5))
            should_inspect_for_child_tile = {
                (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7),
                (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (7, 3), (7, 4), (7, 5), (7, 6), (8, 3), (8, 4), (8, 5), (8, 6)
            }
            self.assertEqual(
                child_node.should_inspect,
                node.should_inspect | should_inspect_for_child_tile - {(6, 5)}
            )

    def test_heuristic_simple_treat(self):
        data = {'p1': [(9, 9)], 'p2': []}
        start_node = Node(player_1='p1', player_2='p2', maximizing_player=False, tiles=data)
        self.heuristic_simple_treat.calculate(start_node)
        # TODO; add assert

    def test_test_(self):
        game = Game.objects.create(player_1='p1', player_2='p2', type=GameType.MULTIPLAYER)
        Tile.objects.create(game_id=game.id, player='p1', x_coordinate=9, y_coordinate=9)
        tiles = Tile.objects.filter(game_id=game.id)
        data = {game.player_1: [], game.player_2: []}
        _ = [data[tile.player].append((tile.x_coordinate, tile.y_coordinate)) for tile in tiles]

        node = Node(player_1=game.player_1, player_2=game.player_2, maximizing_player=False, tiles=data)
        minimax = Minimax(HeuristicSimpleTreat(), GameRules())
        value, node = minimax.calculate_minimax(node, 1)
        # TODO: finish
