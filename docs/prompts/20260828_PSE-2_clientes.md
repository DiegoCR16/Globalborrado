# Registro de Conversación IA (CHIA) - Historia PSE-2

**Fecha:** 28 de Agosto de 2026  
**Historia de Usuario:** PSE-2 - Registro, Alta y Perfil de Cliente (Hito 3 - Fullstack)  
**Asignatura:** Ingeniería de Software 2 - FPUNA (Global Exchange)  

---

## 1. Resumen de la Tarea
Implementación fullstack en Django y Django REST Framework (DRF) para la gestión, registro, alta, segmentación y perfil de clientes en Global Exchange (PSE-2). Incluye el modelo de base de datos `Customer`, endpoints REST completos para registro y consulta con filtrado por segmentación (Minorista, Corporativo, VIP), actualización y desactivación (soft delete), registro persistente de auditoría (`AuditLog`), interfaz gráfica web interactiva en Bootstrap (`customer_admin.html`), y pruebas unitarias completas bajo Pyunit (`django.test`).

---

## 2. Criterios de Aceptación Evaluados
1. **Modelo de Cliente:** Definición del modelo `Customer` con atributos de identificación (nombre, apellido, documento/CI o RUC, email, teléfono, dirección), segmentación (`client_type`: Minorista, Corporativo, VIP) y estado activo/inactivo.
2. **Endpoints REST (DRF):** Creación de endpoints para listado con filtros de segmentación, registro de nuevos clientes (`/api/customers/`), consulta, actualización de perfil y desactivación (`/api/customers/<int:pk>/`).
3. **Auditoría de Operaciones:** Registro persistente de eventos de auditoría en base de datos (`CUSTOMER_CREATED`, `CUSTOMER_UPDATED`, `CUSTOMER_DEACTIVATED`) con trazabilidad de usuario e IP.
4. **Interfaz Gráfica Fullstack:** Plantilla web HTML/Bootstrap para el alta, listado, filtrado y desactivación de clientes (`customer_admin.html`).
5. **Pruebas Unitarias:** Suite de pruebas unitarias (`CustomerManagementTests`) cubriendo todas las operaciones CRUD, segmentación y validación de plantillas con 100% de éxito.

---

## 3. Comandos Utilizados
```bash
# 1. Verificación de rama develop y creación de rama feature/PSE-2
git checkout develop
git checkout -b feature/PSE-2

# 2. Creación y aplicación de migraciones para el módulo de clientes
python manage.py makemigrations authentication
python manage.py migrate

# 3. Ejecución de la suite completa de pruebas unitarias
python manage.py test authentication
```

---

## 4. Evidencia de Pruebas Exitosas
```text
Creating test database for alias 'default'...
..........Found 10 test(s).
System check identified no issues (0 silenced).

----------------------------------------------------------------------
Ran 10 tests in 19.078s

OK
Destroying test database for alias 'default'...
```

**Pruebas unitarias ejecutadas con éxito (100% aprobadas):**
- `test_login_success_retail`: Validación de autenticación SSO para cliente minorista.
- `test_login_success_corporate_with_mfa`: Validación de autenticación con MFA para cliente corporativo.
- `test_login_failed_missing_mfa`: Verificación de rechazo por falta de MFA.
- `test_login_failed_invalid_credentials`: Verificación de rechazo por credenciales inválidas.
- `test_role_crud_and_keycloak_sync`: Validación de CRUD de roles.
- `test_granular_permission_assignment_and_unlinking`: Validación de permisos granulares.
- `test_rbac_access_control_denied`: Validación de control de acceso RBAC.
- `test_roles_admin_ui_template`: Validación de UI de roles.
- `test_customer_registration_and_crud`: Validación de registro, listado con segmentación por tipo (`VIP`), actualización de perfil y desactivación de clientes con auditoría.
- `test_customer_admin_ui_template`: Validación de acceso a la plantilla web de administración de clientes (`customer_admin.html`).

---

## 5. Archivos Modificados / Creados
- `authentication/models.py`: Incorporación del modelo `Customer` con docstrings en formato Google/Sphinx.
- `authentication/serializers.py`: Serializer `CustomerSerializer` para DRF.
- `authentication/views.py`: Vistas DRF y de plantilla (`CustomerListCreateView`, `CustomerDetailView`, `CustomerAdminTemplateView`) documentadas con docstrings.
- `authentication/urls.py` y `globalexchange/urls.py`: Enrutamiento de endpoints y vistas de administración de clientes.
- `authentication/templates/authentication/customer_admin.html`: Interfaz web interactiva en Bootstrap para gestión de clientes.
- `authentication/migrations/0003_customer.py`: Migración de base de datos para el modelo `Customer`.
- `authentication/tests.py`: Suite `CustomerManagementTests`.
- `docs/prompts/20260828_PSE-2_clientes.md`: Registro CHIA obligatorio.
