from .models import *
from django.views.generic.base import *
from django.views.generic import FormView
from .forms import *
from django.core.paginator import Paginator, Page
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
        print(request.POST)
        if cuenta_form.is_valid():
            return self.form_valid(cuenta_form)
        else:
            print(cuenta_form.errors)  # Imprime los errores del formulario
            return self.form_invalid(cuenta_form)

    def form_valid(self, cuenta_form):
        print(cuenta_form.cleaned_data)  # Imprime todos los datos limpiados
        nickname = cuenta_form.cleaned_data.get('nickname')
        foto = cuenta_form.cleaned_data.get('foto')
        email = cuenta_form.cleaned_data.get('email_address')
        contraseña = cuenta_form.cleaned_data.get('password')
        print(nickname)
        print(foto)
        print(email)
        print(contraseña)
        Usuario.objects.create_user(nickname, email, contraseña, foto)
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
    paginator = Paginator(games_random, 5)  # Mostrar 5 juegos por página
    page_number = self.request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['top_videojuegos'] = games_sorted
    context['page_obj'] = page_obj
    return context

class UsersController(TemplateView):
    template_name = 'accounts/allUsers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuarios_populares = Usuario.objects.get_usuarios_populares()[:3]
        usuarios = Usuario.objects.get_remaining_random_usuarios(usuarios_populares)

        # Configurar la paginación
        paginator = Paginator(usuarios, 5)  # Mostrar 10 usuarios por página
        page_number = self.request.GET.get('page')  # Obtener el número de página desde la URL

        # Obtener la página actual
        page_obj = paginator.get_page(page_number)

        context['top_usuarios'] = usuarios_populares
        context['usuarios'] = page_obj  # Pasar la página de usuarios en lugar de la lista completa
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

        # Paginación
        paginator = Paginator(reseñas, 5)  # 5 reseñas por página
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        juegosFavoritos = myuser.reseñas.filter(puntuacion__gte=3).order_by('-puntuacion')[:3]
        context['page_obj'] = page_obj
        context['juegosFavoritos'] = juegosFavoritos
        context['session'] = session
        context['myuser'] = myuser
        context['userinfo'] = myuser
        context['misListas'] = susListas
        context['losigue'] = loSigue
        return context

class ListController(TemplateView):
   template_name='list/lists.html'
   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      listas_sorted = ListaDeJuegos.objects.get_listas_populares()[:4]
      listas = ListaDeJuegos.objects.all()
      paginator = Paginator(listas, 4) 
      page_number = self.request.GET.get('page')  # Obtener el número de página desde la URL
     # Obtener la página actual
      page_obj = paginator.get_page(page_number)
      context['top_listas'] = listas_sorted
      context['listas'] = page_obj
      return context

class ListInfoController(TemplateView):
   template_name = 'list/listContent.html'
   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      list_id = self.kwargs.get('id')
      myList = ListaDeJuegos.objects.get(id=list_id)
      content = EstaEn.objects.filter(lista = myList.id)
      like = Reseña.objects.usuario_le_gusta_lista(self.request, myList)
      context['myList'] = myList
      context['contenido'] = content
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
        context['userinfo'] = usuario
        context['listas'] = listas
        context['session'] = session
        context['losigue'] = loSigue
        return context
  
class ListCreateFormController(FormView):
    template_name = 'forms/crear_lista.html'
    form_class = ListaForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = Usuario.objects.get_user_from_request(self.request)
        self.success_url = reverse_lazy('yourList', kwargs={'id_usuario': usuario.id})
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
        contenido = lista.contenido.all()
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

class DeleteVideojuegoView(View):
    def post(self, request, *args, **kwargs):
        lista_id = kwargs.get('lista_id')
        videojuego_id = request.POST.get('delete_videojuego_id')
        try:
            esta_en = EstaEn.objects.get(videojuego_id=videojuego_id, lista_id=lista_id)
            esta_en.delete()
        except EstaEn.DoesNotExist:
            pass
        return redirect('listFormEdit', pk=lista_id)

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

class SearchController(View):
    form = SearchForm
    query = ""
    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            self.query = query
            search_type = form.cleaned_data['search_type']
            
            # Resultados de la búsqueda
            games_page_obj = []
            users_page_obj = []
            lists_page_obj = []
            
            if search_type == 'games':
                games_page_obj = self.search_games(query,1)
                return render(request, 'search_results.html', {
                'games_page_obj': games_page_obj,
                })
            elif search_type == 'users':
                users_page_obj = self.search_users(query,1)
                return render(request, 'search_results.html', {
                'users_page_obj': users_page_obj,
                })
            elif search_type == 'game_lists':
                lists_page_obj = self.search_lists(query,1)
                return render(request, 'search_results.html', {
                'lists_page_obj': lists_page_obj,
                })
            else:
                games_page_obj = self.search_games(query,1)
                users_page_obj = self.search_users(query,1)
                lists_page_obj = self.search_lists(query,1)
                return render(request, 'search_results.html', {
                'games_page_obj': games_page_obj,
                'users_page_obj': users_page_obj,
                'lists_page_obj': lists_page_obj,
                })

    def get(self, request):
        games_page_number = request.GET.get('games_page')
        users_page_number = request.GET.get('users_page')
        lists_page_number = request.GET.get('lists_page')
        query = self.query
        games_page_obj = []
        users_page_obj = []
        lists_page_obj = []            
        if games_page_number:
                games_page_obj = self.search_games(query,games_page_number)
                return render(request, 'search_results.html', {
                'games_page_obj': games_page_obj,
                })
        elif users_page_number:
                users_page_obj = self.search_users(query,users_page_number)
                return render(request, 'search_results.html', {
                'users_page_obj': users_page_obj,
                })
        elif lists_page_number:
                lists_page_obj = self.search_lists(query,lists_page_number)
                return render(request, 'search_results.html', {
                'lists_page_obj': lists_page_obj,
                })

      
    def search_games(self, query, page):
        games_results = Videojuego.objects.filter(name__icontains=query)
        games_paginator = Paginator(games_results, 5)
        games_page_obj = games_paginator.get_page(page)
        return games_page_obj

    def search_users(self, query, page):
        users_results = Usuario.objects.filter(nickname__icontains=query)
        users_paginator = Paginator(users_results, 5)
        users_page_obj = users_paginator.get_page(page)
        return users_page_obj

    def search_lists(self, query, page):
        lists_results = ListaDeJuegos.objects.filter(name__icontains=query)
        lists_paginator = Paginator(lists_results, 5)
        lists_page_obj = lists_paginator.get_page(page)
        return lists_page_obj
    
class EditarPerfilController(FormView):
    template_name = 'forms/editar_perfil.html'
    form_class = UsuarioEditForm
    
    def get_initial(self):
        initial = super().get_initial()
        usuario = Usuario.objects.get_user_from_request(self.request)
        initial['nickname'] = usuario.nickname
        initial['email_address'] = usuario.cuenta.email
        initial['foto'] = usuario.foto
        self.success_url = reverse_lazy('profile', kwargs={'id': usuario.id})
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session'] = True
        return context
    
    def post(self, request, *args, **kwargs):
        profile_form = self.get_form()
        try:
            print("entro al try")
            print(profile_form.data['email_address'])
            print(profile_form.data['nickname'])
 
            if profile_form.is_valid():
                print("entro al if")
                return self.form_valid(profile_form)
            else:
                ('entro al else')
                return self.form_invalid(profile_form)
        except forms.ValidationError as e:
            print(e)
            profile_form.add_error(None, str(e))
            return self.form_invalid(profile_form)
        except ValueError as e:
            print(e)
            profile_form.add_error(None, str(e))
            return self.form_invalid(profile_form)
        
    def form_valid(self, profile_form):
        usuario = Usuario.objects.get_user_from_request(self.request)
        email = profile_form.data['email_address']
        nickname = profile_form.data['nickname']
        foto = self.request.FILES.get('foto')
        Usuario.objects.edit_user(usuario,nickname,email,foto)
        return redirect(self.success_url)
                  
    def form_invalid(self, profile_form):
        return self.render_to_response(
            self.get_context_data(form=profile_form)
        )