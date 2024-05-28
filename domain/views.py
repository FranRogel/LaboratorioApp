from django.contrib.auth.hashers import make_password
from .models import *
from django.views.generic.base import *
from django.contrib.auth.hashers import make_password
from django.views.generic import FormView,ListView
from .forms import *
from django.urls import reverse_lazy
from django.contrib.auth import login,logout
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
import random
from django.contrib.auth.views import LogoutView
from django.contrib.messages.views import SuccessMessageMixin


class RegistroView(FormView):
    template_name = 'accounts/register.html'
    form_class = CuentaForm
    second_form_class = UsuarioForm
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'usuario_form' not in context:
            context['usuario_form'] = self.second_form_class()
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        cuenta_form = self.get_form()
        usuario_form = self.second_form_class(request.POST, request.FILES)
        if cuenta_form.is_valid() and usuario_form.is_valid():
            return self.form_valid(cuenta_form, usuario_form)
        else:
            return self.form_invalid(cuenta_form, usuario_form)

    def form_valid(self, cuenta_form, usuario_form):
        # Crear y guardar la cuenta
        cuenta = cuenta_form.save(commit=False)
        cuenta.set_password(cuenta_form.cleaned_data['password'])  # Usar set_password para hashear
        cuenta.save()
        
        # Crear y guardar el usuario
        usuario = usuario_form.save(commit=False)
        usuario.cuenta = cuenta
        usuario.save()
        
        return redirect(self.success_url)

    def form_invalid(self, cuenta_form, usuario_form):
        return self.render_to_response(
            self.get_context_data(form=cuenta_form, usuario_form=usuario_form)
        )
    
class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = 'main'
      
    def form_valid(self, form):
        email_Address = form.cleaned_data['email_Address']
        password = form.cleaned_data['password']
        try:
            cuenta = Cuenta.objects.get(email_Address=email_Address)
            if check_password(password, cuenta.password):
                login(self.request, cuenta)  # Aquí usamos cuenta ya que hereda de AbstractBaseUser
                return redirect(self.get_success_url())
            else:
                return self.form_invalid(form)
        except Cuenta.DoesNotExist:
            return self.form_invalid(form)

#class CustomLogoutView(SuccessMessageMixin, LogoutView):
    #template_name = 'accounts/logout.html'  # Opcional: define una plantilla para mostrar un mensaje de confirmación de logout
    #success_message = "Has cerrado sesión con éxito."
    #next_page = 'login'  # Redirige a la página de inicio de sesión después del logout

class MainController(TemplateView):
    template_name = 'main.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myuser'] = Usuario.objects.get_user_from_request(self.request)
        context['usuariosCount'] = Usuario.objects.count()
        context['juegosCount'] = Videojuego.objects.count()
        context['listasCount'] = ListaDeJuegos.objects.count()
        return context

class GamesController(TemplateView):
   template_name = 'games/games.html'
   def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    games_sorted =  Videojuego.objects.get_juegos_populares()[:3]
    games_random = Videojuego.objects.get_remaining_random_juegos(10,games_sorted)
    context['myuser'] = Usuario.objects.get_user_from_request(self.request)
    context['top_videojuegos'] = games_sorted
    context['videojuegos'] = games_random
    return context

class UsersController(TemplateView):
  template_name = 'accounts/allUsers.html'
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    usuarios_populares = Usuario.objects.get_usuarios_populares()[:3]
    usuarios = Usuario.objects.get_remaining_random_usuarios(10,usuarios_populares)
    context['top_usuarios'] = usuarios_populares
    context['usuarios'] = usuarios
    context['myuser'] = Usuario.objects.get_user_from_request(self.request)
    return context

class ProfileController(TemplateView):
  template_name = 'accounts/profile.html'
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    id_usuario = kwargs.get("id")
    myuser = Usuario.objects.get(id=id_usuario)
    user_session = Usuario.objects.get_user_from_request(self.request)
    session = Usuario.objects.session_perfil_match(user_session, myuser)
    loSigue = False  # Inicializamos loSigue como False por defecto
    if session:
            try:
                loSigue = True  
            except Siguen.DoesNotExist:
                loSigue = False
    susListas = myuser.listas_de_juegos.all()
    reseñas = myuser.reseñas.all()
    reseñas_sorted = random.sample(list(reseñas), min(5,reseñas.count()))
    #Preguntar si estas cosas son mejor para el modelo o es muy especifico
    juegosFavoritos = myuser.reseñas.filter(puntuacion__gte=3).order_by('-puntuacion')[:3]
    context['reseñas'] = reseñas_sorted
    context['juegosFavoritos'] = juegosFavoritos
    context['myuser'] = user_session
    context['userinfo'] = myuser
    context['misListas'] = susListas
    context['session'] = user_session
    context['losigue'] = loSigue
    return context

class ListController(TemplateView):
   template_name='list/lists.html'
   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      listas_sorted = ListaDeJuegos.objects.get_listas_populares()[:4]
      random_listas = ListaDeJuegos.objects.get_remaining_random_listas(10,listas_sorted)
      context['myuser'] = Usuario.objects.get_user_from_request(self.request)
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
      context['myList'] = myList
      context['contenido'] = content
      context['myuser'] = Usuario.objects.get_user_from_request(self.request)
      return context

class GameInfoAndReseñaController(View):
    template_name = 'games/gameInfo.html'
    
    def get(self, request, *args, **kwargs):
        game_id = self.kwargs.get('id')
        game = Videojuego.objects.get(id=game_id)
        reseñas = Reseña.objects.filter(game=game)
        usuario = Usuario.objects.get_user_from_request(self.request)
        reseñaExiste = False
        # Verificar si el usuario ya escribió una reseña para este juego
        try:
            reseña_existente = Reseña.objects.get(game=game, writer=usuario)
            # Si existe una reseña, cargar los datos en el formulario
            reseña_form = ReseñaForm(instance=reseña_existente)
            reseñaExiste = True
        except Reseña.DoesNotExist:
            # Si no existe una reseña, crear un formulario vacío
            reseña_form = ReseñaForm()
        
        return render(request, self.template_name, {'myuser' : usuario, 
        'myGame': game, 'reseñas': reseñas, 
        'form': reseña_form, 'existe' : reseñaExiste})

    def post(self, request, *args, **kwargs):
        game_id = self.kwargs.get('id')
        game = Videojuego.objects.get(id=game_id)
        reseñas = Reseña.objects.filter(game=game)
        usuario = Usuario.objects.get_user_from_request(self.request)
        reseña_form = ReseñaForm(request.POST)
        
        if reseña_form.is_valid():
            # Verificar si el usuario ya escribió una reseña para este juego
            try:
                reseña_existente = Reseña.objects.get(game=game, writer=usuario)
                # Si existe una reseña, actualizarla con los nuevos datos
                reseña_form = ReseñaForm(request.POST, instance=reseña_existente)
            except Reseña.DoesNotExist:
                pass
            
            reseña = reseña_form.save(commit=False)
            reseña.game = game
            reseña.writer = usuario
            reseña.save()
            return redirect('game', id=game_id)  # Ajusta esto según tu lógica
        else:
            return render(request, self.template_name, {'myuser' : usuario,'myGame': game, 'reseñas': reseñas, 'form': reseña_form})

class YourGamesController(TemplateView):
   template_name = 'session/your_games.html'
   def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    id_usuario = kwargs.get("id_usuario")
    usuario = Usuario.objects.get(id=id_usuario)
    user_session = Usuario.objects.get_user_from_request(self.request)
    session = Usuario.objects.sesion_perfil_match(user_session,usuario)
    juegos = Videojuego.objects.filter(reseñas__writer=usuario)
    context['juegos'] = juegos
    context['myuser'] = user_session
    context['userinfo'] = usuario
    context['session'] = session
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
        lista_con_contenido = self.get_lista_con_contenido(listas)
        context['myuser'] = user_session
        context['userinfo'] = usuario
        context['listas'] = lista_con_contenido
        context['session'] = session
        return context

    def get_lista_con_contenido(self,listas):
        lista_con_contenido = []
        for lista in listas:
            contenido = lista.contenido.first()  # Obtener el primer elemento de contenido
            if contenido:  # Verificar si hay contenido
                lista_con_contenido.append({
                    'lista': lista,
                    'imagen_url': contenido.videojuego.portada.url,
                    'nombre_videojuego': contenido.videojuego.name,
                })
        return lista_con_contenido
    
class listFormController(FormView):
    template_name = 'forms/crear_lista.html'
    form_class = ListaForm
    second_form_class = EstaEnForm
    success_url = reverse_lazy('yourLists')

    def get_initial(self):
        initial = super().get_initial()
        # Si hay una lista existente, cargar los datos iniciales del formulario con esos valores
        lista_id = self.kwargs.get('lista_id')
        if lista_id:
            lista = ListaDeJuegos.objects.get(id=lista_id)
            self.success_url = reverse_lazy('listFormEdit', kwargs={'lista_id': lista_id})
            initial = lista.__dict__
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasar el usuario autenticado como argumento adicional al formulario
        usuario = Usuario.objects.get_user_from_request(self.request)
        context['myuser'] = usuario
        context['estaEn_form'] = self.second_form_class()
        lista_id = self.kwargs.get('lista_id')
        esPosibleBorrar = False
        if lista_id:
            lista = ListaDeJuegos.objects.get(id=lista_id)
            contenido = lista.contenido.all()[:3]
            context['lista'] = lista
            context['contenidos'] = contenido
            esPosibleBorrar = True
        context['borrar'] = esPosibleBorrar    
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = None
        lista_form = self.get_form()
        estaEn_form = self.second_form_class(request.POST)
        errores = []
        try:
            if lista_form.is_valid() and estaEn_form.is_valid():
                return self.form_valid(lista_form, estaEn_form)
            else:
                return self.form_invalid(lista_form)
        except forms.ValidationError as e:
            errores.append(e)
        except ValueError as e:
            errores.append(e)

    def form_valid(self, lista_form,estaEn_form):
        # Guardar la Lista
        lista_id = self.kwargs.get('lista_id')
        if lista_id:
            # Si hay un ID de lista, significa que estamos editando una lista existente
            lista = ListaDeJuegos.objects.get(id=lista_id)
            lista_form.instance = lista
        else:
            # Si no hay un ID de lista, estamos creando una nueva lista
            lista = lista_form.save(commit=False)
            usuario = Usuario.objects.get(cuenta=self.request.user)
            lista.creator = usuario

        lista.save()
        estaEn_form.instance.lista = lista
        EstaEn.objects.create(videojuego=estaEn_form.instance.videojuego, lista=lista)
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
        usuario_id = kwargs['usuario_id']  # ID del usuario que se está siguiendo
        usuario_a_seguir = Usuario.objects.get(id=usuario_id)
        usuario_session = Usuario.objects.get_user_from_request(self.request)
        # Crear una instancia en el modelo Siguen
        Siguen.objects.create(seguidor=usuario_session, seguido=usuario_a_seguir)
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
        session = Usuario.objects.get_user_from_request(self.request)
        context['myuser'] = session
        context['userinfo'] = usuario
        #Cambiar por sesion_perfil_match
        user_session = False
        if session:
            user_session = user_id == session.id
        #Cambiar
        seguidores_relacion = usuario.seguido_por.all()  # Obtener todas las instancias de Siguen relacionadas con el usuario
        seguidores = [relacion.seguidor for relacion in seguidores_relacion]  # Extraer los seguidores de esas instancias
        context['seguidores'] = seguidores
        context['session'] = user_session
        return context
        
class SeguidosController(TemplateView):
    template_name = "accounts/seguidos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('id')  
        usuario = Usuario.objects.get(id=user_id)
        session = Usuario.objects.get_user_from_request(self.request)
        context['myuser'] = session
        context['userinfo'] = usuario
        #Cambiar por sesion_perfil_match
        user_session = False
        if session:
            user_session = user_id == session.id
        context['session'] = user_session
        seguidos_relacion = usuario.sigue_a.all()  
        seguidos = [relacion.seguido for relacion in seguidos_relacion] 
        context['seguidos'] = seguidos
        return context
    