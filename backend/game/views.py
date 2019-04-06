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
        tiles = Tile.objects.filter(game=tile.game)
        tiles_serializer = self.serializer_class(instance=tiles, many=True)
        return Response(tiles_serializer.data, status.HTTP_201_CREATED)


class NextMoveView(APIView):
    def get(self, request, game_id: int, player: str):  # TODO: validate if it is this user turn
        serializer = NextMoveSerializer(data={"game": game_id, "player": player})
        serializer.is_valid(raise_exception=True)
        game = Game.objects.get(pk=game_id)

        Analyzer.refresh()
        value, chosen_node = self._get_move(game, player)
        self._print_logs(value, chosen_node)

        return Response({'coordinates': chosen_node.new_move if chosen_node else (9, 9)},
                        status.HTTP_200_OK)

    @staticmethod
    @Analyzer.update_time(Analyzer.ALL_TIME)
    def _get_move(game, player):
        data = {game.player_1: [], game.player_2: []}
        for tile in Tile.objects.filter(game=game):
            data[tile.player].append((tile.x_coordinate, tile.y_coordinate))

        node = Node(player_1=game.player_1,
                    player_2=game.player_2,
                    maximizing_player=game.player_1 == player,
                    tiles=data)
        minimax = Minimax(HeuristicSimpleTreat(), GameRules())
        value, chosen_node = minimax.calculate_minimax(node, 3)
        return value, chosen_node

    @staticmethod
    def _print_logs(value: float, node: Node):
        node.print_children(0)
        for tile, line in node.lines.items():
            print(tile, line)
        Analyzer.print_results()
        print(value)
