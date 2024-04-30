from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Cuenta(models.Model):
    password = models.CharField(max_length=30)
    email_Address = models.EmailField(max_length=30, unique=True)

class Usuario(models.Model):
    nickname = models.CharField(max_length=30, unique=True)
    foto = models.FileField(upload_to="uploads/", null=True)
    cuenta = models.OneToOneField(Cuenta, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nickname

class Videojuego(models.Model):
    name = models.CharField(max_length=30, unique=True)
    producer = models.CharField(max_length=30)
    publisher = models.CharField(max_length=30) #Podria ser un diccionario?
    release_Date = models.DateField()
    plataforms = models.CharField(max_length=250) #Podria ser un diccionario?
    portada = models.FileField(upload_to="uploads/",null=True)
    def __str__(self):
        return self.name

class ListaDeJuegos(models.Model):
    name = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=255)
    creator = models.ForeignKey(Usuario, on_delete=models.CASCADE,related_name='listas_de_juegos') #Quiero que las listas sean reconocidas por name+creator preguntarle al profe
    
    def __str__(self):
        return self.name + " " + self.creator.nickname

class Reseña(models.Model):
    title = models.CharField(max_length=30)
    content = models.CharField(max_length=300)
    TAG_CHOICES = [
        ('C', 'Complete'),
        ('P', 'Playing'),
        ('D', 'Drop'),
    ]
    tag = models.CharField(max_length=1, choices=TAG_CHOICES, null=True)
    puntuacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    writer = models.ForeignKey(Usuario,null=True, on_delete=models.SET_NULL)
    game = models.ForeignKey(Videojuego, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class EstaEn(models.Model):
    videojuego = models.ForeignKey(Videojuego, null=True, on_delete=models.SET_NULL)
    lista = models.ForeignKey(ListaDeJuegos, on_delete=models.CASCADE,related_name='contenido')

    def __str__(self):
        return self.lista.name +" "+  self.videojuego.name
    
class LeGusta(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    lista = models.ForeignKey(ListaDeJuegos, on_delete=models.CASCADE, related_name='me_gustan')

class Siguen(models.Model):
    seguidor = models.ForeignKey(Usuario, related_name='sigue_a', on_delete=models.CASCADE)
    seguido = models.ForeignKey(Usuario, related_name='seguido_por', on_delete=models.CASCADE)



