from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import Random
from django.contrib.auth.hashers import make_password
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class UsuarioManager(models.Manager):
    def create_user(self, nickname, email,password, foto):
        if self.verificar_nickname_unico(nickname):
            raise ValueError("Ya existe un usuario con ese nombre")
        
        if not self.verificar_nickname_length(nickname):
            raise ValueError("El nombre debe tener de 2 a 30 caracteres")
        
        passwordhash = make_password(password)
        cuenta = User.objects.create(username=nickname,email=email,password=passwordhash)
        if foto:
            usuario = self.model(
            nickname=nickname,
            cuenta=cuenta,
            foto=foto
            )
        else:
            usuario = self.model(
            nickname=nickname,
            cuenta=cuenta
            )

        usuario.save(using=self._db)
        return usuario

    def edit_user(self, user, nickname, email, foto):
        if (not self.verificar_nickname_unico(nickname)) and (user.nickname == nickname):
            raise ValueError("Ya existe un usuario con ese nombre")
        
        if not self.verificar_nickname_length(nickname):
            raise ValueError("El nombre debe tener de 2 a 30 caracteres")
        
        # Actualizar los campos del modelo Usuario
        user.nickname = nickname
        if foto:
            user.foto = foto
        user.save(using=self._db)
        
        # Actualizar los campos de la cuenta asociada (User)
        cuenta = user.cuenta
        cuenta.username = nickname
        cuenta.email = email
        cuenta.save(using=self._db)

        return user

    def get_user_from_request(self, request):
        if request.user.is_authenticated:
            try:
                return self.get(cuenta=request.user)
            except self.model.DoesNotExist:
                return None
        return None

    def get_usuarios_populares(self):
        usuarios = self.annotate(num_seguidores=Count('seguido_por')).order_by('-num_seguidores')
        return usuarios

    def get_random_usuarios(self):
        return self.order_by(Random())

    def get_random_usuarios_exclude(self, id_session):
        return self.order_by(Random()).exclude(id=id_session)

    def get_remaining_random_usuarios(self, exclude_queryset):
        exclude_ids = exclude_queryset.values_list('id', flat=True)
        return self.get_random_usuarios().exclude(id__in=exclude_ids)

    def sesion_perfil_match(self,user_session,user):
        session=False
        if user_session:
            session = user == user_session
        return session
    
    def verificar_nickname_unico(self, nickname):
        return self.filter(nickname=nickname).exists()

    def verificar_nickname_length(self,nickname):
        return ((len(nickname) > 2) and (len(nickname) <= 30))
    
class Usuario(models.Model):
    nickname = models.CharField(max_length=30, unique=True)
    foto = models.ImageField(upload_to="media/usuarios/", default="media/usuarios/generica.jpg")
    cuenta = models.OneToOneField(User, on_delete=models.CASCADE)
    objects = UsuarioManager()

    def __str__(self):
        return self.nickname
    
    def juegos_favoritos(self):
        reseñas = Reseña.objects.order_by('puntuacion')
        reseñas_usuarios = reseñas.filter(writer=self)
        print(reseñas_usuarios)
        return reseñas_usuarios
    
    def cant_listas_de_juegos(self):
        return self.listas_de_juegos.count()

    def cant_juegos_jugados(self):
        return self.reseñas.count()

    def cant_seguidores(self):
        return self.seguido_por.count()

    def cant_seguidos(self):
        return self.sigue_a.count()
       
class VideojuegoManager(models.Manager):
    def get_random_videojuegos(self, count=1):
        return self.order_by(Random())[:count]
    
    def cant_jugadores(self, videojuego):
        return videojuego.reseñas.count()
    
    def get_juegos_populares(self):
        juegos = self.annotate(num_reseñas=models.Count('reseñas')).order_by('-num_reseñas')
        return juegos
    
    def get_random_juegos(self):
        return self.order_by(Random())

    def get_remaining_random_juegos(self, exclude_queryset):
        exclude_ids = exclude_queryset.values_list('id', flat=True)
        return self.get_random_juegos().exclude(id__in=exclude_ids)

    def puntuacion_promedio(self, videojuego):
        puntuacion_total = sum(reseña.puntuacion for reseña in videojuego.reseñas.all())
        reseña_count = videojuego.reseñas.count()
        return puntuacion_total / reseña_count if reseña_count != 0 else 0
    
    def cant_apariciones_lista(self, videojuego):
        return videojuego.listas.count()
    
class Videojuego(models.Model):
    name = models.CharField(max_length=100, unique=True)
    producer = models.CharField(max_length=30)
    publisher = models.CharField(max_length=30) 
    release_Date = models.DateField()
    plataforms = models.CharField(max_length=250) 
    portada = models.ImageField(upload_to="media/uploads/")
    descripcion = models.CharField(max_length=1500)
    objects = VideojuegoManager()

    def puntuacion_promedio(self):
        puntuacion_total = sum(reseña.puntuacion for reseña in self.reseñas.all())
        reseña_count = self.reseñas.count()
        return round(puntuacion_total / reseña_count) if reseña_count != 0 else 0
    
    def cant_apariciones_lista(self):
        return self.listas.count()
    
    def cant_jugadores(self):
        return self.reseñas.count()

    def __str__(self):
        return self.name

class ListaDeJuegosManager(models.Manager):
    def verificar_name(self,nombre):
        return ((len(nombre) > 2) and (len(nombre) <= 30))

    def verificar_descripcion(self,descripcion):
        return ((len(descripcion) > 2) and (len(descripcion) <= 300))
    
    def create_lista_de_juegos(self,nombre,descripcion,creator):
        if not self.verificar_name(nombre):
            raise ValueError("El nombre debe tener de 2 a 30 caracteres")
        
        if not self.verificar_descripcion(descripcion):
            raise ValueError("La descripcion debe tener de 2 a 300 caracteres")
        
        if self.filter(name=nombre, creator=creator).exists():
            raise ValueError("Ya creaste una lista con ese nombre")

        lista = self.model(
            name = nombre,
            descripcion = descripcion,
            creator = creator
        )

        lista.save()
        return lista

    def update_lista_de_juegos(self,lista,nombre,descripcion,creator):
        if not self.verificar_name(nombre):
            raise ValueError("El nombre debe tener de 2 a 30 caracteres")
        
        if self.filter(name=nombre, creator=creator).exclude(pk=lista.pk).exists():
            raise ValueError("Ya creaste una lista con ese nombre")

        if not self.verificar_descripcion(descripcion):
            raise ValueError("La descripcion debe tener de 2 a 300 caracteres")
        
        lista.name = nombre
        lista.descripcion = descripcion
        lista.save()
        return lista

    def cant_me_gustan_lista(self,lista):
        return lista.me_gustan.count()
    
    def get_listas_populares(self):
        listas = self.annotate(num_me_gustan=models.Count('me_gustan')).order_by('-me_gustan')
        return listas
    
    def get_random_listas(self):
        return self.order_by(Random())

    def get_remaining_random_listas(self,exclude_queryset):
        exclude_ids = exclude_queryset.values_list('id', flat=True)
        return self.get_random_listas().exclude(id__in=exclude_ids)

class ListaDeJuegos(models.Model):
    name = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=300)
    creator = models.ForeignKey(Usuario, on_delete=models.CASCADE,related_name='listas_de_juegos') #Quiero que las listas sean reconocidas por name+creator preguntarle al profe
    objects = ListaDeJuegosManager()

    class Meta:
        unique_together = (('name', 'creator'))

    def __str__(self):
        return self.name
    
    def cantMeGustan(self):
        return self.me_gustan.count()
    
    def cant_juegos(self):
        return self.contenido.count()

    def juegos(self):
        relacion = self.contenido.all()
        print(relacion)
        return relacion

    def primer_juego(self): 
        primer_contenido = self.contenido.first()
        if primer_contenido:
            return primer_contenido.videojuego
        return None 

class LeGusta(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    lista = models.ForeignKey(ListaDeJuegos, on_delete=models.CASCADE, related_name='me_gustan')

class ReseñaManager(models.Manager):
    def verificar_titulo(self,titulo):
        return ((len(titulo) < 2) or (len(titulo) > 30))
    
    def verificar_contenido(self,contenido):
        return (len(contenido) > 500)
    
    def verificar_puntuacion(self,puntuacion):
        return puntuacion < 1 or puntuacion > 5 
    
    def usuario_le_gusta_lista(self,request,lista):
        user = Usuario.objects.get_user_from_request(request)
        if LeGusta.objects.filter(usuario=user, lista=lista):
            return True
        else:
            return False

    def create_reseña(self,titulo,puntuacion,tag,escritor,juego,contenido=""):
        if self.verificar_titulo(titulo):
            raise('Titulo debe tener entre 2 y 30 caracteres')
        if self.verificar_contenido(contenido):
            raise('Contenido no puede sobrepasar los 500 caracteres')
        if self.verificar_puntuacion(puntuacion):
            raise('Puntuacion debe ser un numero entre 1 y 5')
        
        reseña = self.model(
            title = titulo,
            content = contenido,
            puntuacion=puntuacion,
            tag = tag,
            writer = escritor,
            game = juego
        )
        reseña.save()

    def update_reseña(self,reseña,titulo,puntuacion,tag,contenido=""):
        if self.verificar_titulo(titulo):
            raise('Titulo debe tener entre 2 y 30 caracteres')
        if self.verificar_contenido(contenido):
            raise('Contenido no puede sobrepasar los 500 caracteres')
        if self.verificar_puntuacion(puntuacion):
            raise('Puntuacion debe ser un numero entre 1 y 5')
        
        reseña.title=titulo
        reseña.content=contenido
        reseña.puntuacion=puntuacion
        reseña.tag=tag
        reseña.save()

    def get_random_reseñas(self):
        return self.order_by(Random())

class Reseña(models.Model):
    title = models.CharField(max_length=30)
    content = models.CharField(max_length=500, null=True)
    TAG_CHOICES = [
        ('C', 'Complete'),
        ('P', 'Playing'),
        ('D', 'Drop'),
    ]
    tag = models.CharField(max_length=1, choices=TAG_CHOICES, null=True)
    puntuacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    writer = models.ForeignKey(Usuario,null=True, on_delete=models.SET_NULL, related_name = 'reseñas')
    game = models.ForeignKey(Videojuego, on_delete=models.CASCADE, related_name="reseñas")
    objects = ReseñaManager()
    def __str__(self):
        return self.title
    
class EstaEn(models.Model):
    videojuego = models.ForeignKey(Videojuego, null=True, on_delete=models.CASCADE, related_name="listas")
    lista = models.ForeignKey(ListaDeJuegos, on_delete=models.CASCADE,related_name='contenido')

    def __str__(self):
        return self.videojuego.name
    
    def existe_juego(self,juego,lista):
        return lista.contenido.videjuego.filter(id=juego.id)
    class Meta:
        unique_together = (('videojuego', 'lista'))
    
class Siguen(models.Model):
    seguidor = models.ForeignKey(Usuario, related_name='sigue_a', on_delete=models.CASCADE)
    seguido = models.ForeignKey(Usuario, related_name='seguido_por', on_delete=models.CASCADE)
    class Meta:
        unique_together = (('seguidor', 'seguido'))



