from django.contrib import admin
from .models import *
from django.utils.html import format_html


# Register your models here.

class VideojuegoAdmin(admin.ModelAdmin):
    list_display = ('mostrar_foto','name', 'producer', 'publisher', 'release_Date', 'plataforms','descripcion')
    list_filter = ('name', 'producer')
    search_fields = ('name', 'producer')

    def mostrar_foto(self, obj):
        if obj.portada:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.portada.url)
        else:
            return '(No hay foto)'

admin.site.register(Videojuego, VideojuegoAdmin)

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'get_cuenta_email', 'mostrar_foto')
    list_filter = ('nickname', 'cuenta__email')
    search_fields = ('nickname', 'cuenta__email')

    def mostrar_foto(self, obj):
        if obj.foto:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.foto.url)
        else:
            return '(No hay foto)'

    mostrar_foto.short_description = 'Foto'  # Etiqueta para la columna en el admin

    def get_cuenta_email(self, obj):
        return obj.cuenta.email

    get_cuenta_email.admin_order_field = 'cuenta__email'
    get_cuenta_email.short_description = 'Email de Cuenta'

admin.site.register(Usuario, UsuarioAdmin)

class ListaDeJuegosAdmin(admin.ModelAdmin):
    list_display = ('name','descripcion','creator')
    list_filter = ('name', 'creator')
    search_fields = ('name', 'creator')

admin.site.register(ListaDeJuegos, ListaDeJuegosAdmin)

class ReseñaAdmin(admin.ModelAdmin):
    list_display = ('title', 'puntuacion', 'game','writer','tag','content')
    list_filter = ('title', 'puntuacion','game', 'writer','tag')
    search_fields = ('title', 'puntuacion','game', 'writer','tag')

admin.site.register(Reseña, ReseñaAdmin)

class SiguenAdmin(admin.ModelAdmin):
    list_display = ('seguidor','seguido')
    list_filter = ('seguidor','seguido')
    search_fields = ('seguidor','seguido')

admin.site.register(Siguen, SiguenAdmin)

class EstaEnAdmin(admin.ModelAdmin):
    list_display = ('videojuego','lista')
    list_filter = ('videojuego','lista')
    search_fields = ('videojuego','lista')

admin.site.register(EstaEn, EstaEnAdmin)

class LeGustaAdmin(admin.ModelAdmin):
    list_display = ('usuario','lista')
    list_filter = ('usuario','lista')
    search_fields = ('usuario','lista')

admin.site.register(LeGusta, LeGustaAdmin)