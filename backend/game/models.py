from typing import TYPE_CHECKING, List

from django.db import models


if TYPE_CHECKING:
    from game.internal_types import CaptureElement


class Game(models.Model):
    type = models.CharField(max_length=30)
    player_1 = models.CharField(max_length=30)
    player_2 = models.CharField(max_length=30)
    start_date = models.DateTimeField(auto_now_add=True)
    winner = models.CharField(max_length=30, null=True)


class Tile(models.Model):
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()
    player = models.CharField(max_length=30)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
