from rest_framework.views import APIView
from rest_framework.response import Response
from game.serializers import GameSerializer

from django.contrib.auth.models import User


class GameView(APIView):
    def get(self, request):
        return Response()

    # def post(self, re):
