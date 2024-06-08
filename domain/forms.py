from django import forms
from .models import *


class LoginForm(forms.Form):
    email_Address = forms.EmailField(label='Correo Electrónico')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

class UsuarioForm(forms.ModelForm):
    email_address = forms.EmailField(label='Correo Electrónico')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    class Meta:
        model = Usuario
        fields = ['nickname','foto']

class ReseñaForm(forms.ModelForm):
    content = forms.CharField(required=False, widget=forms.Textarea)
    class Meta:
        model = Reseña
        fields = ['title','content','tag','puntuacion']
          
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 2 or len(title) > 30:
            raise forms.ValidationError('El titulo debe tener de 2 a 30 caracteres.')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) > 500:
            raise forms.ValidationError('El contenido sobrepasa los 500 caracteres')
        return content
    
    def clean_puntuacion(self):
        puntuacion = self.cleaned_data.get('puntuacion')
        if puntuacion < 1 or puntuacion > 5:
            raise forms.ValidationError('La puntuacion debe ser un numero entre 1 y 5')
        return puntuacion

class ListaForm(forms.ModelForm):
    descripcion = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = ListaDeJuegos
        fields = ['name','descripcion']
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 2 or len(name) > 30:
            raise forms.ValidationError('El nombre debe tener de 2 a 30 caracteres.')
        return name

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if len(descripcion) < 2 or len(descripcion) > 300:
            raise forms.ValidationError('La descripcion debe tener de 2 a 300 caracteres')
        return descripcion
    
class EstaEnForm(forms.ModelForm):
    lista_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = EstaEn
        fields = ['videojuego', 'lista_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['videojuego'].required = False

    def clean(self):
        cleaned_data = super().clean()
        videojuego = cleaned_data.get('videojuego')
        lista_id = cleaned_data.get('lista_id')
        if lista_id and videojuego:
            if EstaEn.objects.filter(videojuego=videojuego, lista_id=lista_id).exists():
                print('entre al if')
                raise forms.ValidationError("Ya existe una instancia de EstaEn con estos valores.")
        return cleaned_data

class SearchForm(forms.Form):
    SEARCH_CHOICES = [
        ('all', 'Todo'),
        ('games', 'Juegos'),
        ('users', 'Usuarios'),
        ('game_lists', 'Listas de Juegos')
    ]

    query = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'placeholder': '¿Que estas pensando?...'
    }))
    search_type = forms.ChoiceField(choices=SEARCH_CHOICES, required=True)



