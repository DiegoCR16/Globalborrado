import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'globalexchange.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile, SystemPermission, Role

# Crear usuarios de prueba si no existen
if not User.objects.filter(username='admin').exists():
    u_admin = User.objects.create_superuser(username='admin', email='admin@globalexchange.com', password='password123')
    UserProfile.objects.create(user=u_admin, role='ADMIN')
    print("Usuario Administrador creado: admin / password123")

if not User.objects.filter(username='cliente_minorista').exists():
    u1 = User.objects.create_user(username='cliente_minorista', password='password123')
    UserProfile.objects.create(user=u1, role='RETAIL_CLIENT')
    print("Usuario creado: cliente_minorista / password123 (Sin MFA obligatorio)")

if not User.objects.filter(username='cliente_corporativo').exists():
    u2 = User.objects.create_user(username='cliente_corporativo', password='password123')
    UserProfile.objects.create(user=u2, role='CORPORATE_CLIENT')
    print("Usuario creado: cliente_corporativo / password123 (Con MFA obligatorio)")

# Crear permisos de sistema por defecto si no existen
perms = [
    ('MANAGE_ROLES', 'Gestionar Roles', 'Crear, listar, modificar y desactivar roles'),
    ('OPERATE_EXCHANGE', 'Operar Divisas', 'Ejecutar compra y venta de divisas'),
    ('VIEW_HISTORY', 'Ver Historial', 'Consultar historial de transacciones y auditoría'),
]
for code, name, desc in perms:
    SystemPermission.objects.get_or_create(code=code, defaults={'name': name, 'description': desc})

print("\n¡Datos de prueba y permisos listos!")
print("Puedes iniciar sesión con:")
print(" - Admin: admin / password123")
print(" - Minorista: cliente_minorista / password123")
print(" - Corporativo: cliente_corporativo / password123 (Requiere mfa_token: 123456)")
