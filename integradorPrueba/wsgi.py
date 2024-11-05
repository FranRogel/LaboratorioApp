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
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'integradorPrueba.settings')  # Cambié a setdefault para mayor robustez

# Asegúrate de que el entorno de Django esté configurado
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # Esto puede ayudar a identificar problemas de configuración
    raise RuntimeError("Error al inicializar la aplicación WSGI: " + str(e))
