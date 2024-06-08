from django.contrib import admin
from .models import *
admin.site.register(Usuario)
admin.site.register(ListaDeJuegos)
admin.site.register(Reseña)
admin.site.register(EstaEn)
admin.site.register(LeGusta)
admin.site.register(Siguen)
# Register your models here.

class VideojuegoAdmin(admin.ModelAdmin):
    list_display = ('name', 'producer', 'publisher', 'release_Date', 'plataforms', 'portada','descripcion')
    list_filter = ('name', 'producer')
    search_fields = ('name', 'producer')

admin.site.register(Videojuego, VideojuegoAdmin)

