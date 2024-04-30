from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('register/', views.registerPage, name='register'),
    path('games/', views.games, name='games'),
    path('games/gameInfo/<int:id>', views.gameInfo, name='game'),
    path('users/', views.users, name='users'),
    path('users/profile/<int:id>', views.profile, name='profile'),
    path('users/profile/listContent/<int:id>', views.listContent, name='listContent'), #Preguntar como hago para evitar que se alargue la url
    path('users/profile/listContent/game/<int:id>', views.gameInfo, name='game')
]