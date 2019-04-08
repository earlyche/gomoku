from typing import TYPE_CHECKING, List

from django.db import models


if TYPE_CHECKING:
    from game.internal_types import Capture


class Game(models.Model):
    type = models.CharField(max_length=30)
    player_1 = models.CharField(max_length=30)
    player_2 = models.CharField(max_length=30)
    start_date = models.DateTimeField(auto_now_add=True)
    winner = models.CharField(max_length=30, null=True)

    def remove_capture(self, capture: List['Capture'], maximizing_player: bool):
        index = 0
        player_symbol = 'x' if maximizing_player else 'o'
        opponent_symbol = 'o' if maximizing_player else 'x'

        while index < len(capture) - 3:
            if capture[index].symbol == player_symbol and capture[index + 3].symbol == player_symbol \
                    and capture[index + 1].symbol == opponent_symbol and capture[index + 2].symbol == opponent_symbol:

                Tile.objects.filter(game=self,
                                    x_coordinate=capture[index + 1].tile[0],
                                    y_coordinate=capture[index + 1].tile[1]).delete()
                Tile.objects.filter(game=self,
                                    x_coordinate=capture[index + 2].tile[0],
                                    y_coordinate=capture[index + 2].tile[1]).delete()
                index += 3
            else:
                index += 1


class Tile(models.Model):
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()
    player = models.CharField(max_length=30)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
