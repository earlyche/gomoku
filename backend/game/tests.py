from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from game.types import GameType
from game.models import Game, Tile


class GameTestCase(TestCase):
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
