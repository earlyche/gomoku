from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from game.serializers import GameSerializer, TileSerializer
from game.models import Tile


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
    serializer_class = TileSerializer

    def get(self, request, game_id, user_id):
        # todo: check is it this user turn

        response = {
            'coordinates': (2, 4)
        }
        return Response(response, status.HTTP_200_OK)

