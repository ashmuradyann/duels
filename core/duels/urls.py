from django.urls import path
from .views import OpenDuels, CompletedDuelsCount, AllDuelsByToken, CreateDuel, AllMaps, DuelContesting, DuelsByStatus

urlpatterns = [
    # path("", index, name="index"),
    path('maps/', AllMaps.as_view(), name='all-maps'),
    path('all/', AllDuelsByToken.as_view(), name='all-duels'),
    path('open/', OpenDuels.as_view(), name='open-duels'),
    path('completed/', CompletedDuelsCount.as_view(), name='completed-duels'),
    path('create/', CreateDuel.as_view(), name='create-duel'),
    path('duel-contesting/', DuelContesting.as_view(), name='contesting-duel'),
    path('duels/', DuelsByStatus.as_view(), name='contenting-duel'),
]
