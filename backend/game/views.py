import time
import pickle

import redis
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from game.serializers import GameSerializer, TileSerializer
from game.models import Tile, Game
from game.node import Node
from game.algorithm import Minimax
from game.heuristics import HeuristicSimpleTreat
from game.rules import GameRules
from game.time_analyzer import TimeAnalyzer


time_analyzer = TimeAnalyzer()
print(time_analyzer)


class GameView(GenericAPIView):
    serializer_class = GameSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.error_messages, status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class TileView(GenericAPIView):
    serializer_class = TileSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.error_messages, status.HTTP_400_BAD_REQUEST)
        tile = serializer.save()
        tiles = Tile.objects.filter(game=tile.game)
        tiles_serializer = self.serializer_class(instance=tiles, many=True)
        return Response(tiles_serializer.data, status.HTTP_201_CREATED)


class NextMoveView(APIView):
    def get(self, request, game_id: int, player: str):
        # TODO: validate if it is this user turn, and user existence

        time_analyzer.refresh()

        if not Game.objects.filter(pk=game_id).exists():
            return Response({'game_id': "Game not found"}, status.HTTP_404_NOT_FOUND)
        game = Game.objects.get(pk=game_id)
        if player != game.player_1 and player != game.player_2:
            return Response({'game_id': "No such player"}, status.HTTP_400_BAD_REQUEST)

        data = {game.player_1: [], game.player_2: []}
        for tile in Tile.objects.filter(game_id=game_id):
            data[tile.player].append((tile.x_coordinate, tile.y_coordinate))
        node = Node(player_1=game.player_1,
                    player_2=game.player_2,
                    maximizing_player=game.player_1 == player,
                    tiles=data)
        minimax = Minimax(HeuristicSimpleTreat(), GameRules())

        time1 = time.time()
        value, chosen_node = minimax.calculate_minimax(node, 3)
        time_analyzer.update(time_analyzer.ALL_TIME, time.time() - time1)

        node.print_children(0)
        for tile, line in chosen_node.lines.items():
            print(tile, line)
        time_analyzer.print_results()
        print(value)

        redis_conn = redis.StrictRedis(port=6379)
        redis_conn.set('node_tree', pickle.dumps(node))
        response = {
            'coordinates': chosen_node.new_move if node else (9, 9)
        }
        return Response(response, status.HTTP_200_OK)

