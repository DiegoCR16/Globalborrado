import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'globalexchange.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile

# Crear usuarios de prueba si no existen
if not User.objects.filter(username='cliente_minorista').exists():
    u1 = User.objects.create_user(username='cliente_minorista', password='password123')
    UserProfile.objects.create(user=u1, role='RETAIL_CLIENT')
    print("Usuario creado: cliente_minorista / password123 (Sin MFA obligatorio)")

if not User.objects.filter(username='cliente_corporativo').exists():
    u2 = User.objects.create_user(username='cliente_corporativo', password='password123')
    UserProfile.objects.create(user=u2, role='CORPORATE_CLIENT')
    print("Usuario creado: cliente_corporativo / password123 (Con MFA obligatorio)")

print("\n¡Usuarios listos para pruebas! Ejecuta el servidor con:")
print("python manage.py runserver")
