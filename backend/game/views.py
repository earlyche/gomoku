from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from game.serializers import GameSerializer, TileSerializer, NextMoveSerializer
from game.models import Tile, Game
from game.node import Node
from game.algorithm import Minimax
from game.heuristics import HeuristicSimpleTreat
from game.rules import GameRules
from game.analyzer import Analyzer
from game.internal_types import TileXY


class GameView(GenericAPIView):
    serializer_class = GameSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class TileView(GenericAPIView):
    serializer_class = TileSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        tile = serializer.save()

        node = Node.from_game(game=tile.game, player=tile.player)

        print(node.find_captures_to_delete(tile_xy=TileXY.from_serializer(tile)))
        for capture in node.find_captures_to_delete(tile_xy=TileXY.from_serializer(tile)):
            print(capture)
            Tile.objects.filter(game=tile.game,
                                x_coordinate__in=(capture[0].x, capture[1].x),
                                y_coordinate__in=(capture[0].y, capture[1].y),).delete()

        winner = GameRules().is_terminated(node)

        tiles = Tile.objects.filter(game=tile.game)
        tiles_serializer = self.serializer_class(instance=tiles, many=True)
        return Response(
            {
                "tiles": tiles_serializer.data,
                "winner": winner,
            },
            status.HTTP_201_CREATED,
        )


class NextMoveView(APIView):
    serializer_class = NextMoveSerializer

    def get(self, request, game_id: int, player: str):  # TODO: validate if it is this user turn
        serializer = self.serializer_class(data={"game": game_id, "player": player})
        serializer.is_valid(raise_exception=True)
        game = Game.objects.get(pk=game_id)

        Analyzer.refresh()
        value, chosen_node = self._get_move(game, player)
        self._print_logs(value, chosen_node)

        return Response(
            {
                'coordinates': chosen_node.new_move if chosen_node else (9, 9),
                'time': Analyzer.get(Analyzer.ALL_TIME),
            },
            status.HTTP_200_OK
        )

    @staticmethod
    @Analyzer.update_time(Analyzer.ALL_TIME)
    def _get_move(game, player):
        node = Node.from_game(game, player)
        minimax = Minimax(HeuristicSimpleTreat())
        value, chosen_node = minimax.calculate_minimax(node, 2)
        return value, chosen_node

    @staticmethod
    def _print_logs(value: float, node: Node):
        if not node:
            return
        node.print_children(0)
        Analyzer.print_results()
        print(value)
