from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path("publishers/", views.publishers, name="publishers"),
    path("platforms/", views.platforms, name="platforms"),
    path("genres/", views.genres, name="genres"),
    path("games/", views.games, name="games"),
    path("sales/", views.sales, name="sales"),

    path("games/add/", views.game_create, name="game_add"),
    path("games/<int:pk>/edit/", views.game_update, name="game_edit"),
    path("games/<int:pk>/delete/", views.game_delete, name="game_delete"),
]
