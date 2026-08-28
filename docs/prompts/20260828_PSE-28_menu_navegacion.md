# Registro de Conversación IA (CHIA) - Historia PSE-28

**Fecha:** 28 de Agosto de 2026  
**Historia de Usuario:** PSE-28 - Menú Principal y Navegación Dinámica (Hito 3 - Fullstack)  
**Asignatura:** Ingeniería de Software 2 - FPUNA (Global Exchange)  

---

## 1. Resumen de la Tarea
Implementación fullstack en Django y Django REST Framework (DRF) para el menú principal y barra de navegación dinámica en Global Exchange (PSE-28). Incluye la vista API `/api/menu/` que provee la estructura de menú y permisos personalizados según el rol del usuario autenticado (integrando PSE-26 de roles, PSE-4 de autenticación SSO/MFA, PSE-2/PSE-3 de clientes y PSE-6 de límites y KYC), interfaz gráfica web interactiva en Bootstrap (`main_menu.html`), vista de plantilla protegida (`/menu/`), registro persistente de auditoría, y suite completa de pruebas unitarias bajo Pyunit (`django.test`).

---

## 2. Criterios de Aceptación Evaluados
1. **Línea Gráfica y Estándares Visuales:** Diseño de la interfaz del menú principal respetando los estándares visuales y la línea gráfica unificada en Bootstrap (`main_menu.html`).
2. **Renderizado Dinámico de Menú:** Implementación de la vista API `/api/menu/` que despliega únicamente los módulos y opciones permitidos para el rol del usuario autenticado (Administrador, Cliente Corporativo, Cliente Minorista, Analista Cambiario).
3. **Información de Usuario y Cierre de Sesión:** Visualización del nombre de usuario, rol activo y provisión de un botón seguro para cerrar sesión (`secureLogout`).
4. **Navegación Fluida:** Enlaces directos y tarjetas de acceso rápido a los diferentes módulos autorizados manteniendo la persistencia de la sesión.
5. **Seguridad y Control de Acceso:** Restricción de acceso mediante autenticación (`IsAuthenticated`) en endpoints y vistas de menú.
6. **Pruebas Unitarias:** Suite de pruebas unitarias (`UserMenuNavigationTests`) verificando el API de menú para rol administrador y corporativo, y el acceso exitoso a la plantilla web de navegación con 100% de éxito.

---

## 3. Comandos Utilizados
```bash
# 1. Verificación de rama develop y creación de rama feature/PSE-28
git checkout develop
git checkout -b feature/PSE-28

# 2. Ejecución de la suite completa de pruebas unitarias
python manage.py test
```

---

## 4. Evidencia de Pruebas Exitosas
```text
Creating test database for alias 'default'...
.......................Found 23 test(s).
System check identified no issues (0 silenced).

----------------------------------------------------------------------
Ran 23 tests in 23.449s

OK
Destroying test database for alias 'default'...
```

**Pruebas unitarias ejecutadas con éxito (100% aprobadas):**
- Pruebas de Autenticación SSO y MFA (PSE-4): `test_login_success_retail`, `test_login_success_corporate_with_mfa`, `test_login_failed_missing_mfa`, `test_login_failed_invalid_credentials`.
- Pruebas de Roles y Permisos Granulares (PSE-26): `test_role_crud_and_keycloak_sync`, `test_granular_permission_assignment_and_unlinking`, `test_rbac_access_control_denied`, `test_roles_admin_ui_template`.
- Pruebas de Gestión de Clientes (PSE-2): `test_customer_registration_and_crud`, `test_customer_admin_ui_template`.
- Pruebas de Personas Jurídicas y Clasificación (PSE-3): `test_corporate_customer_registration_success`, `test_corporate_registration_weak_password`, `test_corporate_registration_duplicate_email`, `test_customer_classification_and_segmentation`, `test_corporate_customer_admin_ui_template`.
- Pruebas de Límites Transaccionales y Cumplimiento KYC (PSE-6): `test_transaction_limit_parameterization`, `test_transaction_validation_success_and_kyc_alert`, `test_transaction_validation_limit_exceeded`, `test_kyc_alert_status_update`, `test_kyc_limits_admin_ui_template`.
- Pruebas de Menú Principal y Navegación Dinámica (PSE-28):
  - `test_user_menu_api_admin`: Validación de opciones administrativas en el API de menú para rol ADMIN.
  - `test_user_menu_api_corporate`: Validación de opciones corporativas en el API de menú para rol CORPORATE_CLIENT.
  - `test_main_menu_template_view`: Validación de acceso a la plantilla web del menú principal (`main_menu.html`).

---

## 5. Archivos Modificados / Creados
- `authentication/views.py`: Implementación de las clases `UserMenuView` y `MainMenuTemplateView` con docstrings en formato Google/Sphinx.
- `authentication/urls.py` y `globalexchange/urls.py`: Enrutamiento para el endpoint `/api/menu/` y la vista web `/menu/`.
- `authentication/templates/authentication/main_menu.html`: Interfaz web interactiva en Bootstrap para el menú principal y navegación dinámica por rol.
- `authentication/tests.py`: Suite `UserMenuNavigationTests`.
- `docs/prompts/20260828_PSE-28_menu_navegacion.md`: Registro CHIA obligatorio.
