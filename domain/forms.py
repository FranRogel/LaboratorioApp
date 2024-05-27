from django import forms
from .models import *


class LoginForm(forms.Form):
    email_Address = forms.EmailField(label='Correo Electrónico')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ['email_Address', 'password']

    # Añadir confirmación de contraseña
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden")
        
        return cleaned_data
    
    def save(self, commit=True):
        cuenta = super().save(commit=False)
        cuenta.set_password(self.cleaned_data['password'])
        if commit:
            cuenta.save()
        return cuenta

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nickname', 'foto']

class ReseñaForm(forms.ModelForm):
    class Meta:
        model = Reseña
        fields = ['title','content','tag','puntuacion',]

class ListaForm(forms.ModelForm):
    def __init__(self, *args, usuario=None, **kwargs):
        self.usuario = usuario 
        super().__init__(*args, **kwargs)
    class Meta:
        model = ListaDeJuegos
        fields = ['name','descripcion']

class EstaEnForm(forms.ModelForm):
    class Meta:
        model = EstaEn
        fields = ['videojuego']
    def clean(self):
        cleaned_data = super().clean()
        videojuego = cleaned_data.get('videojuego')
        lista = cleaned_data.get('lista')

        # Verificar si ya existe una instancia con los mismos valores
        if EstaEn.objects.filter(videojuego=videojuego, lista=lista).exists():
            raise forms.ValidationError("Ya existe una instancia de EstaEn con estos valores.")

        return cleaned_data
    



