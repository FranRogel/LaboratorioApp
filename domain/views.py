from .models import *
from django.views.generic.base import *
from django.views.generic import FormView
from .forms import *
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
import random
from django.contrib.auth.views import LogoutView
from django.contrib.messages.views import SuccessMessageMixin

class RegistroView(FormView):
    template_name = 'accounts/register.html'
    form_class = UsuarioForm
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        cuenta_form = self.get_form()
        if cuenta_form.is_valid():
            return self.form_valid(cuenta_form)
        else:
            return self.form_invalid(cuenta_form)

    def form_valid(self, cuenta_form):
        nickname = cuenta_form.cleaned_data['nickname']
        foto = cuenta_form.cleaned_data['foto']
        email = cuenta_form.cleaned_data['email_address']
        contraseña = cuenta_form.cleaned_data['password']
        Usuario.objects.create_user(nickname,email,contraseña,foto)
        return redirect(self.success_url)

    def form_invalid(self, cuenta_form):
        return self.render_to_response(
            self.get_context_data(form=cuenta_form)
        )
    
class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = 'main'
      
    def form_valid(self, form):
        email_Address = form.cleaned_data['email_Address']
        password = form.cleaned_data['password']
        try:
            usuario = Usuario.objects.get(cuenta__email=email_Address)
            if check_password(password, usuario.cuenta.password):
                print("entre al if")
                login(self.request, usuario.cuenta)  
                return redirect(self.get_success_url())
            else:
                print("fallo el login")
                return self.form_invalid(form)
        except Usuario.DoesNotExist:
            print("fallo el formulario")
            return self.form_invalid(form)

class CustomLogoutView(SuccessMessageMixin, LogoutView):
    template_name = 'accounts/logout.html'  # Opcional: define una plantilla para mostrar un mensaje de confirmación de logout
    success_message = "Has cerrado sesión con éxito."
    next_page = 'login'  # Redirige a la página de inicio de sesión después del logout

class MainController(TemplateView):
    template_name = 'main.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_session = Usuario.objects.get_user_from_request(self.request)
        context['user_session'] = user_session
        context['usuariosCount'] = Usuario.objects.count()
        context['juegosCount'] = Videojuego.objects.count()
        context['listasCount'] = ListaDeJuegos.objects.count()
        context['juegos'] = Videojuego.objects.get_random_juegos()[:5]
        if user_session:
            context['usuarios'] = Usuario.objects.get_random_usuarios_exclude(user_session.id)[:5]
        else:
            context['usuarios'] = Usuario.objects.get_random_usuarios()[:5]
        context['listas'] = ListaDeJuegos.objects.get_random_listas()[:5]
        context['reseñas'] = Reseña.objects.get_random_reseñas()[:5]
        return context

class GamesController(TemplateView):
   template_name = 'games/games.html'
   def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    games_sorted =  Videojuego.objects.get_juegos_populares()[:3]
    games_random = Videojuego.objects.get_remaining_random_juegos(games_sorted)
    context['user_session'] = Usuario.objects.get_user_from_request(self.request)
    context['top_videojuegos'] = games_sorted
    context['videojuegos'] = games_random
    return context

class UsersController(TemplateView):
  template_name = 'accounts/allUsers.html'
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    usuarios_populares = Usuario.objects.get_usuarios_populares()[:3]
    usuarios = Usuario.objects.get_remaining_random_usuarios(usuarios_populares)[:10]
    context['top_usuarios'] = usuarios_populares
    context['usuarios'] = usuarios
    context['user_session'] = Usuario.objects.get_user_from_request(self.request)
    return context

class ProfileController(TemplateView):
  template_name = 'accounts/profile.html'
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    id_usuario = kwargs.get("id")
    myuser = Usuario.objects.get(id=id_usuario)
    user_session = Usuario.objects.get_user_from_request(self.request)
    session = Usuario.objects.sesion_perfil_match(user_session, myuser)
    loSigue = Siguen.objects.filter(seguidor=user_session, seguido=myuser).exists()
    susListas = myuser.listas_de_juegos.all()
    reseñas = myuser.reseñas.all()
    reseñas_sorted = random.sample(list(reseñas), min(5,reseñas.count()))
    #Preguntar si estas cosas son mejor para el modelo o es muy especifico
    juegosFavoritos = myuser.reseñas.filter(puntuacion__gte=3).order_by('-puntuacion')[:3]
    context['reseñas'] = reseñas_sorted
    context['juegosFavoritos'] = juegosFavoritos
    context['session'] = session
    context['myuser'] = myuser
    context['userinfo'] = myuser
    context['misListas'] = susListas
    context['user_session'] = user_session
    context['losigue'] = loSigue
    return context

class ListController(TemplateView):
   template_name='list/lists.html'
   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      listas_sorted = ListaDeJuegos.objects.get_listas_populares()[:4]
      random_listas = ListaDeJuegos.objects.get_remaining_random_listas(listas_sorted)[:10]
      context['user_session'] = Usuario.objects.get_user_from_request(self.request)
      context['top_listas'] = listas_sorted
      context['listas'] = random_listas
      return context

class ListInfoController(TemplateView):
   template_name = 'list/listContent.html'
   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      list_id = self.kwargs.get('id')
      myList = ListaDeJuegos.objects.get(id=list_id)
      content = EstaEn.objects.filter(lista = myList.id)
      user_session = Usuario.objects.get_user_from_request(self.request)
      like = Reseña.objects.usuario_le_gusta_lista(myList,user_session)
      context['myList'] = myList
      context['contenido'] = content
      context['user_session'] = user_session
      context['like'] = like
      return context

class GameInfoAndReseñaController(View):
    template_name = 'games/gameInfo.html'

    def get(self, request, *args, **kwargs):
        return self.render_with_form(request)

    def post(self, request, *args, **kwargs):
        game_id = self.kwargs.get('id')
        game = Videojuego.objects.get(id=game_id)
        usuario = Usuario.objects.get_user_from_request(request)
        reseña_form = ReseñaForm(request.POST)
        
        if reseña_form.is_valid():
            titulo = reseña_form.cleaned_data['title']
            contenido = reseña_form.cleaned_data['content']
            tag = reseña_form.cleaned_data['tag']
            puntuacion = reseña_form.cleaned_data['puntuacion']
            
            try:
                reseña_existente = Reseña.objects.get(game=game, writer=usuario)
                Reseña.objects.update_reseña(reseña_existente, titulo,puntuacion,tag,contenido)
            except Reseña.DoesNotExist:
                Reseña.objects.create_reseña(titulo, puntuacion, tag, usuario, game, contenido)
                
        return self.render_with_form(request, reseña_form)

    def render_with_form(self, request, reseña_form=None):
        game_id = self.kwargs.get('id')
        game = Videojuego.objects.get(id=game_id)
        reseñas = Reseña.objects.filter(game=game)
        usuario = Usuario.objects.get_user_from_request(request)
        reseñaExiste = False
        
        if reseña_form is None:
            try:
                reseña_existente = Reseña.objects.get(game=game, writer=usuario)
                reseña_form = ReseñaForm(instance=reseña_existente)
                reseñaExiste = True
            except Reseña.DoesNotExist:
                reseña_form = ReseñaForm()
                
        context = {
            'user_session': usuario,
            'myGame': game,
            'reseñas': reseñas,
            'form': reseña_form,
            'existe': reseñaExiste
        }
        
        return render(request, self.template_name, context)   
            
class YourGamesController(TemplateView):
   template_name = 'session/your_games.html'
   def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    id_usuario = kwargs.get("id_usuario")
    usuario = Usuario.objects.get(id=id_usuario)
    user_session = Usuario.objects.get_user_from_request(self.request)
    session = Usuario.objects.sesion_perfil_match(user_session,usuario)
    juegos = Videojuego.objects.filter(reseñas__writer=usuario)
    loSigue = Siguen.objects.filter(seguidor=user_session, seguido=usuario).exists()
    context['juegos'] = juegos
    context['userinfo'] = usuario
    context['user_session'] = user_session
    context['session'] = session
    context['losigue'] = loSigue
    return context

class YourListController(TemplateView):
    template_name = 'session/your_lists.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_usuario = kwargs.get("id_usuario")
        usuario = Usuario.objects.get(id=id_usuario)
        user_session = Usuario.objects.get_user_from_request(self.request)
        session = Usuario.objects.sesion_perfil_match(user_session,usuario)
        listas = usuario.listas_de_juegos.all()
        loSigue = Siguen.objects.filter(seguidor=user_session, seguido=usuario).exists()
        #lista_con_contenido = self.get_lista_con_contenido(listas)
        context['user_session'] = user_session
        context['userinfo'] = usuario
        context['listas'] = listas
        context['session'] = session
        context['losigue'] = loSigue
        return context

    def get_lista_con_contenido(self,listas):
        lista_con_contenido = []
        for lista in listas:
            contenido = lista.contenido.first()  # Obtener el primer elemento de contenido
            if contenido:  # Verificar si hay contenido
                lista_con_contenido.append({
                    'lista': lista,
                    'imagen': contenido.videojuego.portada,
                    'nombre_videojuego': contenido.videojuego.name,
                })
        print(lista_con_contenido)
        return lista_con_contenido
    
class ListCreateFormController(FormView):
    template_name = 'forms/crear_lista.html'
    form_class = ListaForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = Usuario.objects.get_user_from_request(self.request)
        self.success_url = reverse_lazy('yourList', kwargs={'id_usuario': usuario.id})
        context['user_session'] = usuario
        context['update'] = False
        return context
    
    def post(self, request, *args, **kwargs):
        lista_form = self.get_form()
        try:
            if lista_form.is_valid():
                return self.form_valid(lista_form)
            else:
                return self.form_invalid(lista_form)
        except forms.ValidationError as e:
            lista_form.add_error(None, str(e))
            return self.form_invalid(lista_form)
        except ValueError as e:
            lista_form.add_error(None, str(e))
            return self.form_invalid(lista_form)

    def form_valid(self, lista_form):
        nombre = lista_form.cleaned_data['name']
        descripcion = lista_form.cleaned_data['descripcion']
        creator = Usuario.objects.get_user_from_request(self.request)
        ListaDeJuegos.objects.create_lista_de_juegos(nombre,descripcion,creator)
        usuario = Usuario.objects.get_user_from_request(self.request)
        return redirect('yourLists', id_usuario=usuario.id)

    def form_invalid(self, lista_form):
        return self.render_to_response(
            self.get_context_data(form=lista_form)
        )

class ListEditFormController(FormView):
    template_name = 'forms/crear_lista.html'
    form_class = ListaForm
    second_form_class = EstaEnForm

    def get_initial(self):
        initial = super().get_initial()
        lista_id = self.kwargs.get('pk')
        lista = ListaDeJuegos.objects.get(id=lista_id)
        self.success_url = reverse_lazy('listFormEdit', kwargs={'pk': lista_id})
        initial.update(lista.__dict__)
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = Usuario.objects.get_user_from_request(self.request)
        lista_id = self.kwargs.get('pk')
        lista = ListaDeJuegos.objects.get(id=lista_id)
        self.second_form_class = EstaEnForm()
        #Hacer esto en el manager EstaEn
        videojuegos_excluidos = EstaEn.objects.filter(lista=lista).values_list('videojuego_id', flat=True)
        videojuegos_queryset = Videojuego.objects.exclude(id__in=videojuegos_excluidos)
        self.second_form_class.fields['videojuego'].queryset = videojuegos_queryset
        ###
        contenido = lista.contenido.all()[:3]
        context['user_session'] = usuario
        context['lista'] = lista
        context['contenidos'] = contenido
        context['estaEn_form'] = self.second_form_class
        context['update'] = True
        return context
    
    def post(self, request, *args, **kwargs):
        lista_form = self.get_form()
        lista_id = self.kwargs.get('pk')

        post_data = request.POST.copy()
        post_data['lista_id'] = lista_id
        esta_en_form = self.second_form_class(post_data)
        try:
            if lista_form.is_valid() and esta_en_form.is_valid():
                return self.form_valid(lista_form, esta_en_form)
            else:
                return self.form_invalid(lista_form)
        except forms.ValidationError as e:
            lista_form.add_error(None, str(e))
            return self.form_invalid(lista_form)
        except ValueError as e:
            lista_form.add_error(None, str(e))
            return self.form_invalid(lista_form)
        
    def form_valid(self, lista_form, esta_en_form):
        lista_id = self.kwargs.get('pk')
        lista = ListaDeJuegos.objects.get(id=lista_id)
        nombre = lista_form.cleaned_data['name']
        descripcion = lista_form.cleaned_data['descripcion']
        creator = Usuario.objects.get_user_from_request(self.request)
        ListaDeJuegos.objects.update_lista_de_juegos(lista, nombre, descripcion, creator)
        videojuego = esta_en_form.cleaned_data['videojuego'] 
        if videojuego:
            EstaEn.objects.create(videojuego=videojuego, lista=lista)
        return redirect(self.success_url)
                  
    def form_invalid(self, lista_form):
        return self.render_to_response(
            self.get_context_data(form=lista_form)
        )

class ListaDeleteFormController(FormView):
    template_name = 'forms/crear_lista.html'
    def post(self,request,*args,**kwargs):
        lista_id = self.kwargs.get('lista_id')
        lista = ListaDeJuegos.objects.get(id = lista_id)
        usuario = Usuario.objects.get_user_from_request(self.request)
        lista.delete()
        return redirect('profile', id=usuario.id)

class SiguenController(FormView):
    template_name = "accounts/profile.html"

    def post(self, request, *args, **kwargs):
        usuario_session = Usuario.objects.get_user_from_request(self.request)
        if not usuario_session:
            return redirect('login')
        usuario_id = kwargs['usuario_id']  # ID del usuario que se está siguiendo
        usuario_a_seguir = Usuario.objects.get(id=usuario_id)
        # Crear una instancia en el modelo Siguen
        Siguen.objects.create(seguidor=usuario_session, seguido=usuario_a_seguir)
        
        # Verificar si hay un parámetro 'next' en la solicitud
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)  # Redirigir al usuario a la URL almacenada en 'next'
        else:
            return redirect('profile', id=usuario_id)
    
class DejarDeSeguirController(FormView):
    template_name = "accounts/profile.html"
    def post(self, request, *args, **kwargs):
        usuario_id = kwargs['usuario_id']  # ID del usuario que se sigue
        usuario_a_seguir = Usuario.objects.get(id=usuario_id)
        usuario_session = Usuario.objects.get_user_from_request(self.request)
        # Borra la instancia del modelo Siguen
        follow = Siguen.objects.filter(seguidor=usuario_session, seguido=usuario_a_seguir)
        follow.delete()
                # Verificar si hay un parámetro 'next' en la solicitud
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)  # Redirigir al usuario a la URL almacenada en 'next'
        else:
            return redirect('profile', id=usuario_id)

class BorrarReseñaController(FormView):
    template_name = 'games/gameInfo.html'
    def post(self,request,*args,**kwargs):
        game_id = kwargs['id']
        usuario = Usuario.objects.get_user_from_request(self.request)
        reseña = Reseña.objects.filter(writer = usuario, game__id = game_id)
        reseña.delete()
        return redirect('game', game_id)

class SeguidoresController(TemplateView):
    template_name = "accounts/seguidores.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('id')  
        usuario = Usuario.objects.get(id=user_id)
        user_session = Usuario.objects.get_user_from_request(self.request)
        loSigue = Siguen.objects.filter(seguidor=user_session, seguido=usuario).exists()
        session = Usuario.objects.sesion_perfil_match(user_session,usuario)
        seguidores_relacion = usuario.seguido_por.all()
        seguidores = [relacion.seguidor for relacion in seguidores_relacion]
        follows = self.get_seguidores_con_follow_session(seguidores, user_session)
        context['seguidores'] = seguidores
        context['session'] = session
        context['losigue'] = loSigue
        context['follows'] = follows
        context['user_session'] = user_session
        context['userinfo'] = usuario
        return context
    
    def get_seguidores_con_follow_session(self,seguidores,user_session):
        follows = []
        for seguidor in seguidores:
            follow = Siguen.objects.filter(seguidor=user_session, seguido=seguidor).exists() 
            follows.append({
                    'seguidor' : seguidor,
                    'follow': follow
                })
        print(follows)
        return follows
        
class SeguidosController(TemplateView):
    template_name = "accounts/seguidos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('id')  
        usuario = Usuario.objects.get(id=user_id)
        user_session = Usuario.objects.get_user_from_request(self.request)
        loSigue = Siguen.objects.filter(seguidor=user_session, seguido=usuario).exists()
        seguidos_relacion = usuario.sigue_a.all()  
        seguidos = [relacion.seguido for relacion in seguidos_relacion] 
        follows = self.get_seguidores_con_follow_session(seguidos, user_session)
        context['seguidos'] = follows
        context['losigue'] = loSigue
        context['user_session'] = user_session
        context['userinfo'] = usuario
        context['session'] = Usuario.objects.sesion_perfil_match(user_session,usuario)
        return context

    def get_seguidores_con_follow_session(self,seguidos,user_session):
        follows = []
        for seguidor in seguidos:
            follow = Siguen.objects.filter(seguidor=user_session, seguido=seguidor).exists() 
            follows.append({
                    'user' : seguidor,
                    'follow': follow
                })
        print(follows)
        return follows
    
class MeGustaListaController(TemplateView):
    template_name="list/listContent.html"
    def post(self, request, *args, **kwargs):
        lista_id = kwargs['id']  
        lista_actual = ListaDeJuegos.objects.get(id=lista_id)
        usuario_session = Usuario.objects.get_user_from_request(self.request)
        LeGusta.objects.create(usuario=usuario_session, lista=lista_actual)
        return redirect('listContent', id=lista_id)

class QuitarMeGustaListaController(TemplateView):
    template_name="list/listContent.html"
    def post(self, request, *args, **kwargs):
        lista_id = kwargs['id']
        lista_actual = ListaDeJuegos.objects.get(id=lista_id)
        usuario_session = Usuario.objects.get_user_from_request(self.request)
        like = LeGusta.objects.filter(usuario=usuario_session, lista=lista_actual)
        like.delete()
        return redirect('listContent', id=lista_id)

def search_view(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_type = form.cleaned_data['search_type']
            games_results = []
            users_results = []
            lists_results = []
            user_session = Usuario.objects.get_user_from_request(request)
            if search_type == 'games':
                games_results = Videojuego.objects.filter(name__icontains=query)
            elif search_type == 'users':
                users_results = Usuario.objects.filter(nickname__icontains=query)
            elif search_type == 'game_lists':
                lists_results = ListaDeJuegos.objects.filter(name__icontains=query)
            else:
                games_results = Videojuego.objects.filter(name__icontains=query)
                users_results = Usuario.objects.filter(nickname__icontains=query)
                lists_results = ListaDeJuegos.objects.filter(name__icontains=query)
            return render(request, 'search_results.html', 
                          {'games' : games_results,
                           'users' : users_results,
                           'lists' : lists_results,
                           'user_session': user_session })
