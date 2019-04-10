from django.db import models


class Game(models.Model):
    type = models.CharField(max_length=30)
    player_1 = models.CharField(max_length=30)
    player_2 = models.CharField(max_length=30)
    start_date = models.DateTimeField(auto_now_add=True)
    winner = models.CharField(max_length=30, null=True)
    captures_x = models.PositiveIntegerField(default=0)
    captures_o = models.PositiveIntegerField(default=0)


class Tile(models.Model):
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()
    player = models.CharField(max_length=30)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
