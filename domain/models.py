from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models import Count
from django.db.models.functions import Random

class CuentaManager(BaseUserManager):
    def create_user(self, email_Address, password, **extra_fields):
        if not self.verificar_email(email_Address):
            raise ValueError('El Email debe tener mas de 2 caracteres')
        email_Address = self.normalize_email(email_Address)
        if not self.verificar_contraseña(password):
            raise ValueError('La contraseña debe tener entre 8 y 30 caracteres')
        user = self.model(email_Address=email_Address, **extra_fields)
        user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, email_Address, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email_Address, password, **extra_fields)
    
    def verificar_email(email_Address):
        return email_Address.len() > 2
    
    def verificar_contraseña(password):
        return ((password > 8) and (password < 30))

class Cuenta(AbstractBaseUser, PermissionsMixin):
    email_Address = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CuentaManager()

    USERNAME_FIELD = 'email_Address'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email_Address

class UsuarioManager(models.Manager):
    def create_user(self, nickname, cuenta, foto):
        if self.verificar_nickname_unico(nickname):
            raise ValueError("Ya existe un usuario con ese nombre")
        
        if self.verificar_nickname_length(nickname):
            raise ValueError("El nombre debe tener de 2 a 30 caracteres")
        
        usuario = self.model(
            nickname=nickname,
            cuenta=cuenta,
            foto=foto
        )

        usuario.save(using=self._db)
        return usuario

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

    def get_random_usuarios(self, count=1):
        return self.order_by(Random())[:count]

    def get_remaining_random_usuarios(self, num, exclude_queryset):
        exclude_ids = exclude_queryset.values_list('id', flat=True)
        return self.get_random_usuarios(num).exclude(id__in=exclude_ids)

    def sesion_perfil_match(self,user_session,user):
        session=False
        if user_session:
            session = user == user_session
        return session
    
    def cant_listas_de_juegos(self, usuario):
        return usuario.listas_de_juegos.count()

    def cant_juegos_jugados(self, usuario):
        return usuario.reseñas.count()

    def cant_seguidores(self, usuario):
        return usuario.seguido_por.count()

    def cant_seguidos(self, usuario):
        return usuario.sigue_a.count()

    def verificar_nickname_unico(self, nickname):
        return not self.filter(nickname=nickname).exists()

    def verificar_nickname_length(self,nickname):
        return not ((nickname.len() > 2) and (nickname.len() <= 30))
    
class Usuario(models.Model):
    nickname = models.CharField(max_length=30, unique=True)
    foto = models.FileField(upload_to="media/uploads/", null=True, default="media/usuarios/yu_foto_perfil.jpg")
    cuenta = models.OneToOneField(Cuenta, on_delete=models.CASCADE)
    objects = UsuarioManager()

class VideojuegoManager(models.Manager):
    def get_random_videojuegos(self, count=1):
        return self.order_by(Random())[:count]
    
    def cant_jugadores(self, videojuego):
        return videojuego.reseñas.count()
    
    def get_juegos_populares(self):
        juegos = self.annotate(num_reseñas=models.Count('reseñas')).order_by('-num_reseñas')
        return juegos
    
    def get_random_juegos(self, count=1):
        return self.order_by(Random())[:count]

    def get_remaining_random_juegos(self, num, exclude_queryset):
        exclude_ids = exclude_queryset.values_list('id', flat=True)
        return self.get_random_juegos(num).exclude(id__in=exclude_ids)

    def puntuacion_promedio(self, videojuego):
        puntuacion_total = sum(reseña.puntuacion for reseña in videojuego.reseñas.all())
        reseña_count = videojuego.reseñas.count()
        return puntuacion_total / reseña_count if reseña_count != 0 else 0
    
    def cant_apariciones_lista(self, videojuego):
        return videojuego.listas.count()
    
class Videojuego(models.Model):
    name = models.CharField(max_length=30, unique=True)
    producer = models.CharField(max_length=30)
    publisher = models.CharField(max_length=30) 
    release_Date = models.DateField()
    plataforms = models.CharField(max_length=250) 
    portada = models.FileField(upload_to="media/uploads/",null=True)
    descripcion = models.CharField(max_length=1500, null=True)
    objects = VideojuegoManager()

    def __str__(self):
        return self.name

    
class ListaDeJuegosManager(models.Manager):
    def verificar_name(self,nombre):
        return ((nombre.len() > 2) and (nombre.len <= 30))

    def verificar_descripcion(self,descripcion):
        return ((descripcion > 2) and (descripcion <= 300))
    
    def create_lista_de_juegos(self,nombre,descripcion,creator):
        if not self.verificar_name(nombre):
            raise ValueError("El nombre debe tener de 2 a 30 caracteres")
        
        if not self.verificar_descripcion(descripcion):
            raise ValueError("La descripcion debe tener de 2 a 300 caracteres")
        
        if self.filter(nombre = nombre, creator = creator):
            raise ValueError("Ya creaste una lista con ese nombre")

        lista = self.model(
            name = nombre,
            descripcion = descripcion,
            creator = creator
        )

        lista.save(using=self._db)
        return lista

    def cant_me_gustan_lista(self,lista):
        return lista.me_gustan.count()
    
    def get_listas_populares(self):
        listas = self.annotate(num_me_gustan=models.Count('me_gustan')).order_by('-me_gustan')
        return listas
    
    def get_random_listas(self, count=1):
        return self.order_by(Random())[:count]

    def get_remaining_random_listas(self, num, exclude_queryset):
        exclude_ids = exclude_queryset.values_list('id', flat=True)
        return self.get_random_listas(num).exclude(id__in=exclude_ids)

class ListaDeJuegos(models.Model):
    name = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=300)
    creator = models.ForeignKey(Usuario, on_delete=models.CASCADE,related_name='listas_de_juegos') #Quiero que las listas sean reconocidas por name+creator preguntarle al profe
    objects = ListaDeJuegosManager()

    class Meta:
        unique_together = (('name', 'creator'))

    def __str__(self):
        return self.name + " " + self.creator.nickname
    
    def cantMeGustan(self):
        return self.me_gustan.count()

class Reseña(models.Model):
    title = models.CharField(max_length=30)
    content = models.CharField(max_length=300, null=True)
    TAG_CHOICES = [
        ('C', 'Complete'),
        ('P', 'Playing'),
        ('D', 'Drop'),
    ]
    tag = models.CharField(max_length=1, choices=TAG_CHOICES, null=True)
    puntuacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    writer = models.ForeignKey(Usuario,null=True, on_delete=models.SET_NULL, related_name = 'reseñas')
    game = models.ForeignKey(Videojuego, on_delete=models.CASCADE, related_name="reseñas")

    def __str__(self):
        return self.title
    
class EstaEn(models.Model):
    videojuego = models.ForeignKey(Videojuego, null=True, on_delete=models.CASCADE, related_name="listas")
    lista = models.ForeignKey(ListaDeJuegos, on_delete=models.CASCADE,related_name='contenido')

    def __str__(self):
        return self.lista.name +" "+  self.videojuego.name
    class Meta:
        unique_together = (('videojuego', 'lista'))
    
class LeGusta(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    lista = models.ForeignKey(ListaDeJuegos, on_delete=models.CASCADE, related_name='me_gustan')

class Siguen(models.Model):
    seguidor = models.ForeignKey(Usuario, related_name='sigue_a', on_delete=models.CASCADE)
    seguido = models.ForeignKey(Usuario, related_name='seguido_por', on_delete=models.CASCADE)
    class Meta:
        unique_together = (('seguidor', 'seguido'))



