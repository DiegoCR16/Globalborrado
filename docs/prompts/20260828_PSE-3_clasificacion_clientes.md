# Registro de Conversación IA (CHIA) - Historia PSE-3

**Fecha:** 28 de Agosto de 2026  
**Historia de Usuario:** PSE-3 - Registro de Clientes Personas Jurídicas y Clasificación/Segmentación (Hito 3 - Fullstack)  
**Asignatura:** Ingeniería de Software 2 - FPUNA (Global Exchange)  

---

## 1. Resumen de la Tarea
Implementación fullstack en Django y Django REST Framework (DRF) para el registro de Personas Jurídicas (clientes corporativos) con delegación a Keycloak, validación estricta de RUC, correo electrónico corporativo y contraseña segura (mínimo 8 caracteres, mayúsculas, minúsculas y caracteres especiales), verificación de duplicidad, módulo de clasificación y segmentación de clientes (`RETAIL`, `CORPORATE`, `VIP`), registro de eventos de auditoría (`AuditLog`), interfaz gráfica web interactiva en Bootstrap (`corporate_customer_admin.html`), y suite completa de pruebas unitarias bajo Pyunit (`django.test`).

---

## 2. Criterios de Aceptación Evaluados
1. **Registro de Personas Jurídicas:** Creación de endpoint y lógica de negocio para registrar empresas solicitando nombre de empresa, RUC, correo corporativo y contraseña, con delegación simulada a Keycloak y sincronización (`keycloak_synced=True`).
2. **Validación de Datos y Seguridad:** Validación de RUC numérico válido, máscara de correo corporativo (`texto@dominio.extensión`), seguridad de contraseña (min 8 caracteres con mayúsculas, minúsculas y caracteres especiales), y denegación si el email o RUC ya se encuentra registrado.
3. **Clasificación y Segmentación de Clientes:** Implementación de endpoints DRF para listar métricas de segmentación (`segmentation_summary`) y reclasificar dinámicamente perfiles de clientes (`RETAIL`, `CORPORATE`, `VIP`).
4. **Auditoría de Operaciones:** Registro persistente de eventos de seguridad y gestión corporativa (`CORPORATE_CUSTOMER_REGISTERED`, `CORPORATE_CUSTOMER_REGISTRATION_FAILED`, `CUSTOMER_RECLASSIFIED`) con trazabilidad de usuario e IP.
5. **Interfaz Gráfica Fullstack:** Plantilla web HTML/Bootstrap para el registro de personas jurídicas y visualización de la clasificación y segmentación de clientes (`corporate_customer_admin.html`).
6. **Pruebas Unitarias:** Suite de pruebas unitarias (`CorporateCustomerSegmentationTests`) cubriendo registro exitoso, validación de contraseñas débiles, rechazo por duplicidad, clasificación y segmentación, y renderizado de plantillas con 100% de éxito.

---

## 3. Comandos Utilizados
```bash
# 1. Verificación de rama develop y creación de rama feature/PSE-3
git checkout develop
git checkout -b feature/PSE-3

# 2. Creación y aplicación de migraciones para soporte de personas jurídicas y segmentación
python manage.py makemigrations authentication
python manage.py migrate

# 3. Ejecución de la suite completa de pruebas unitarias
python manage.py test
```

---

## 4. Evidencia de Pruebas Exitosas
```text
Creating test database for alias 'default'...
...............Found 15 test(s).
System check identified no issues (0 silenced).

----------------------------------------------------------------------
Ran 15 tests in 16.656s

OK
Destroying test database for alias 'default'...
```

**Pruebas unitarias ejecutadas con éxito (100% aprobadas):**
- Pruebas de Autenticación SSO y MFA (PSE-4): `test_login_success_retail`, `test_login_success_corporate_with_mfa`, `test_login_failed_missing_mfa`, `test_login_failed_invalid_credentials`.
- Pruebas de Roles y Permisos Granulares (PSE-26): `test_role_crud_and_keycloak_sync`, `test_granular_permission_assignment_and_unlinking`, `test_rbac_access_control_denied`, `test_roles_admin_ui_template`.
- Pruebas de Gestión y Perfil de Clientes (PSE-2): `test_customer_registration_and_crud`, `test_customer_admin_ui_template`.
- Pruebas de Personas Jurídicas y Clasificación/Segmentación (PSE-3):
  - `test_corporate_customer_registration_success`: Validación de registro corporativo con RUC y contraseña segura con delegación a Keycloak.
  - `test_corporate_registration_weak_password`: Verificación de rechazo ante contraseñas inseguras (< 8 caracteres, sin especiales).
  - `test_corporate_registration_duplicate_email`: Verificación de denegación ante correos duplicados.
  - `test_customer_classification_and_segmentation`: Validación de resumen de segmentación y reclasificación de clientes.
  - `test_corporate_customer_admin_ui_template`: Validación de acceso a la plantilla web corporativa (`corporate_customer_admin.html`).

---

## 5. Archivos Modificados / Creados
- `authentication/models.py`: Ampliación del modelo `Customer` con campos `company_name`, `ruc`, y `keycloak_synced` (Docstrings en formato Google/Sphinx).
- `authentication/serializers.py`: Serializers `CustomerSerializer` y `CorporateCustomerRegisterSerializer` con validaciones de RUC, email corporativo y contraseñas seguras.
- `authentication/views.py`: Vistas DRF y de plantilla (`CorporateCustomerRegisterView`, `CustomerClassificationView`, `CorporateCustomerAdminTemplateView`) documentadas con docstrings.
- `authentication/urls.py` y `globalexchange/urls.py`: Enrutamiento de endpoints corporativos y vistas de administración GUI.
- `authentication/templates/authentication/corporate_customer_admin.html`: Interfaz web interactiva en Bootstrap para registro de personas jurídicas y segmentación de clientes.
- `authentication/migrations/0004_customer_company_name_customer_keycloak_synced_and_more.py`: Migración de base de datos.
- `authentication/tests.py`: Suite `CorporateCustomerSegmentationTests`.
- `docs/prompts/20260828_PSE-3_clasificacion_clientes.md`: Registro CHIA obligatorio.
