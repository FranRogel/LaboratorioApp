"""
WSGI config for integradorPrueba project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""
import os
import sys

# Añade el directorio de tu proyecto al path
path = '/home/frandev/LaboratorioApp'
if path not in sys.path:
    sys.path.append(path)

# Establece la variable de entorno para Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'integradorPrueba.settings'  # Asegúrate de que esto sea correcto

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
