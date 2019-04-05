from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from game.models import Game, Tile
from game.internal_types import GameType


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'type', 'player_1', 'player_2')

    def validate(self, attrs):
        if attrs["player_1"] == attrs["player_2"]:
            raise serializers.ValidationError("Usernames of two players can't be the same")
        return attrs

    @staticmethod
    def validate_type(type_param):
        try:
            GameType(type_param)
        except ValueError:
            raise serializers.ValidationError(f"Should be in {[game_type.value for game_type in GameType]}")
        return type_param


class TileSerializer(serializers.ModelSerializer):
    x_coordinate = serializers.IntegerField(min_value=0, max_value=18)
    y_coordinate = serializers.IntegerField(min_value=0, max_value=18)
    game_id = serializers.IntegerField()

    class Meta:
        model = Tile
        fields = ('x_coordinate', 'y_coordinate', 'game_id', 'player')
        validators = [
            UniqueTogetherValidator(
                queryset=Tile.objects.all(),
                fields=('x_coordinate', 'y_coordinate', 'game_id')
            )
        ]

    def validate(self, attrs):
        game = Game.objects.filter(pk=attrs['game_id']).get()
        if attrs['player'] != game.player_1 and attrs['player'] != game.player_2:
            raise serializers.ValidationError("No such player")
        return attrs

    @staticmethod
    def validate_game_id(game_id):
        try:
            Game.objects.filter(pk=game_id).get()
        except Game.DoesNotExist:
            raise serializers.ValidationError("Game not found")
        return game_id


class NextMoveSerializer(serializers.Serializer):
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())
    player = serializers.CharField()

    def validate(self, attrs):
        game = attrs["game"]
        player = attrs["player"]
        if player != game.player_1 and player != game.player_2:
            raise serializers.ValidationError(f"No such player '{player}'")
        return attrs
