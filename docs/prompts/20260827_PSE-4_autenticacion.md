# Registro de Conversación IA (CHIA) - Historia PSE-4

**Fecha:** 27 de Agosto de 2026  
**Historia de Usuario:** PSE-4 - Inicio de Sesión Único (SSO) y Autenticación de Doble Factor  
**Asignatura:** Ingeniería de Software 2 - FPUNA (Global Exchange)  

---

## 1. Resumen de la Tarea
Implementación del backend en Django para la autenticación SSO y MFA/iToken simulada e integrada con Keycloak (estándares OIDC/JWT), incluyendo perfiles de usuario por roles (Administrador, Cliente Corporativo, Cliente Minorista), registro obligatorio de auditoría para accesos exitosos y fallidos, y pruebas unitarias completas bajo Pyunit (`django.test`).

---

## 2. Criterios de Aceptación Evaluados
1. **SSO y Keycloak:** Autenticación de usuarios validada mediante estándares de arquitectura JWT/OIDC.
2. **MFA Obligatorio:** Exigencia obligatoria de autenticación de doble factor (iToken/MFA) para roles corporativos y administrativos.
3. **Panel Personalizado:** Derivación y visualización de opciones personalizadas (simular, operar compra/venta, ver historial).
4. **Auditoría de Seguridad:** Registro persistente en base de datos de los intentos de inicio de sesión fallidos, credenciales inválidas y errores de MFA.

---

## 3. Comandos Utilizados
```bash
# 1. Crear rama de funcionalidad segun Git Flow
git checkout -b feature/PSE-4

# 2. Instalación de dependencias (Django, DRF, PyJWT)
pip install django djangorestframework django-environ pyjwt cryptography

# 3. Creación de la aplicación de autenticación en Django
python manage.py startapp authentication

# 4. Generación y aplicación de migraciones de base de datos
python manage.py makemigrations authentication
python manage.py migrate

# 5. Ejecución de la suite de pruebas unitarias (Pyunit)
python manage.py test
```

---

## 4. Evidencia de Pruebas Exitosas
```text
Creating test database for alias 'default'...
....Found 4 test(s).
System check identified no issues (0 silenced).

----------------------------------------------------------------------
Ran 4 tests in 7.347s

OK
Destroying test database for alias 'default'...
```

**Pruebas unitarias ejecutadas con éxito (100% aprobadas):**
- `test_login_success_retail`: Validación de inicio de sesión exitoso sin MFA para clientes minoristas.
- `test_login_success_corporate_with_mfa`: Validación de inicio de sesión exitoso con token MFA (iToken) válido para clientes corporativos.
- `test_login_failed_missing_mfa`: Verificación de denegación de acceso (403 Forbidden) ante la ausencia de MFA requerido y registro de auditoría correspondiente (`LOGIN_FAILED_MFA`).
- `test_login_failed_invalid_credentials`: Verificación de denegación de acceso (401 Unauthorized) ante credenciales incorrectas y registro de auditoría (`LOGIN_FAILED`).

---

## 5. Archivos Modificados / Creados
- `authentication/models.py`: Modelos `UserProfile` (roles y MFA) y `AuditLog` (auditoría).
- `authentication/views.py`: Vistas DRF `KeycloakSSOLoginView` y `DashboardView` con docstrings en formato Google/Sphinx.
- `authentication/urls.py`: Enrutamiento de endpoints API.
- `globalexchange/settings.py` y `globalexchange/urls.py`: Configuración del proyecto e inclusión de la app `authentication`.
- `authentication/tests.py`: Suite completa de pruebas unitarias (`AuthenticationTests`).
- `docs/prompts/20260827_PSE-4_autenticacion.md`: Registro CHIA.
