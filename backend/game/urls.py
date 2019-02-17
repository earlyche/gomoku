from django.urls import path

from game.views import GameView, TileView, NextMoveView

urlpatterns = [
    path('', GameView.as_view(), name='game'),
    path('add_tile/', TileView.as_view(), name='tile'),
    path('<int:game_id>/next_move/<int:user_id>/', NextMoveView.as_view(), name='next_move'),
]
