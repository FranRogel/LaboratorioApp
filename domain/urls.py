from django.urls import path
from .import views
from .views import *

urlpatterns = [
    path('', MainController.as_view(), name='main'),
    path('register/', RegistroView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('games/', GamesController.as_view(), name='games'),
    path('lists/',ListController.as_view(), name='lists'),
    path('users/', UsersController.as_view(), name='users'),
    path('gameInfo/<int:id>/', GameInfoAndReseñaController.as_view(), name='game'),
    path('yourGames/<int:id_usuario>/', YourGamesController.as_view(), name='yourGames'),
    path('yourList/<int:id_usuario>/', YourListController.as_view(),name='yourLists'),
    path('listForm/', ListCreateFormController.as_view(),name='listForm'),
    path('listForm/<int:pk>/', ListEditFormController.as_view(),name='listFormEdit'),
    path('delete-videojuego/<int:lista_id>/', DeleteVideojuegoView.as_view(), name='deleteVideojuego'),
    path('profile/<int:id>', ProfileController.as_view(), name='profile'),
    path('seguir/<int:usuario_id>/', SiguenController.as_view(), name='seguir_usuario'),
    path('dejarDeSeguir/<int:usuario_id>/', DejarDeSeguirController.as_view(), name='dejarSeguirUsuario'),
    path('borrarLista/<int:lista_id>/', ListaDeleteFormController.as_view(), name='borrarlista'),
    path('borrarReseña/<int:id>', BorrarReseñaController.as_view(), name='borrarReseña'),
    path('listContent/<int:id>', ListInfoController.as_view(), name='listContent'),
    path('megusta/<int:id>', MeGustaListaController.as_view(), name='like'),
    path('nomegusta/<int:id>', QuitarMeGustaListaController.as_view(), name='unlike'),
    path('followers/<int:id>', SeguidoresController.as_view(), name="followers"),
    path('follow/<int:id>', SeguidosController.as_view(),name='follow'),
    path('editar/', EditarPerfilController.as_view(), name='edit_profile'),
    path('search/', SearchController.as_view(), name='search_view'),
    
]