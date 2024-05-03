from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .forms import CreateUserForm
from .models import *

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password

def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
                # Guardar el usuario
                form.save()

                # Guardar la cuenta
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password1')
                cuenta = Cuenta(email_Address=email, password=make_password(password))
                cuenta.save()

                # Guardar el usuario personalizado
                usuario = Usuario(nickname=form.cleaned_data.get('username'), cuenta=cuenta)
                usuario.save()

                # Redirigir al usuario a alguna página de éxito
                return redirect('/users/')

    # Si el formulario no es válido o es un GET, renderizar la página de registro
    return render(request, 'accounts/register.html', {'form': form})

def main(request):
  template = loader.get_template('main.html')
  return HttpResponse(template.render())

def games(request):
  myGames = Videojuego.objects.all().values()
  template = loader.get_template("games.html")
  context = {
    'myGames' : myGames
  }
  return HttpResponse(template.render(context,request))

def users(request):
  myUsers = Usuario.objects.all().values()
  template = loader.get_template('accounts/allUsers.html')
  context = {
   "myUsers" : myUsers
  }
  return HttpResponse(template.render(context,request))

def profile(request, id):
  myuser = Usuario.objects.get(id=id)
  susListas = myuser.listas_de_juegos.all()
      # Inicializa una lista vacía para almacenar todos los juegos asociados a las listas de juegos
  template = loader.get_template('accounts/profile.html')
  context = {
    'myuser': myuser,
    'misListas' : susListas,
  }
  return HttpResponse(template.render(context,request))

def listContent(request,id):
  myList = ListaDeJuegos.objects.get(id=id)
  content = EstaEn.objects.filter(lista = myList.id)
  template = loader.get_template('listContent.html')
  context = {
    'myList': myList,
    'contenido' : content
  }
  return HttpResponse(template.render(context,request))

def gameInfo(request, id):
  myGame = Videojuego.objects.get(id=id)
  resenias = Reseña.objects.filter(game = myGame)
  template = loader.get_template("gameInfo.html")
  context={
    'myGame' : myGame,
    'reseñas' : resenias 
  }
  return HttpResponse(template.render(context,request))
