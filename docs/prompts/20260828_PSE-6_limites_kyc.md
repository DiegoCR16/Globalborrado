# Registro de Conversación IA (CHIA) - Historia PSE-6

**Fecha:** 28 de Agosto de 2026  
**Historia de Usuario:** PSE-6 - Validación de Límites Transaccionales por Perfil de Cliente y Gestión de Alertas KYC (Hito 3 - Fullstack)  
**Asignatura:** Ingeniería de Software 2 - FPUNA (Global Exchange)  

---

## 1. Resumen de la Tarea
Implementación fullstack en Django y Django REST Framework (DRF) para la validación de límites transaccionales por perfil de cliente, parametrización de límites por tipo de cliente (`RETAIL`, `CORPORATE`, `VIP`), generación automática de alertas de cumplimiento KYC (transacciones de alto valor > 50M PYG o exceso de límites), gestión de estado de alertas KYC (Pendiente, En Revisión, Resuelto), registro persistente de auditoría (`AuditLog`), interfaz gráfica web interactiva en Bootstrap (`kyc_limits_admin.html`), y suite completa de pruebas unitarias bajo Pyunit (`django.test`).

---

## 2. Criterios de Aceptación Evaluados
1. **Parametrización de Límites Transaccionales:** Creación del modelo `TransactionLimit` y endpoints DRF para configurar montos mínimos, máximos y límites diarios por perfil de cliente.
2. **Validación de Transacciones y Límites:** Implementación del endpoint `/api/transactions/validate-limit/` que valida si el monto de la operación cumple con las reglas del perfil y rechaza operaciones fuera de rango.
3. **Gestión y Generación de Alertas KYC:** Creación del modelo `KYCAlert` y lógica para generar automáticamente alertas de cumplimiento (`HIGH_VALUE_TRANSACTION`, `LIMIT_EXCEEDED`) y endpoints DRF para consultar y actualizar el estado de las alertas (`PENDING`, `REVIEWED`, `RESOLVED`).
4. **Auditoría de Operaciones:** Registro persistente de eventos de cumplimiento y parametrización (`TRANSACTION_LIMIT_UPDATED`, `KYC_ALERT_UPDATED`) con trazabilidad de usuario e IP.
5. **Interfaz Gráfica Fullstack:** Plantilla web HTML/Bootstrap para la parametrización de límites y visualización/gestión de alertas KYC (`kyc_limits_admin.html`).
6. **Pruebas Unitarias:** Suite de pruebas unitarias (`KYCLimitsAndComplianceTests`) cubriendo parametrización de límites, validación exitosa, rechazo por exceso de límites con alerta KYC, generación de alerta de alto valor, actualización de estado de alertas y renderizado de plantillas con 100% de éxito.

---

## 3. Comandos Utilizados
```bash
# 1. Verificación de rama develop y creación de rama feature/PSE-6
git checkout develop
git checkout -b feature/PSE-6

# 2. Creación y aplicación de migraciones para límites transaccionales y alertas KYC
python manage.py makemigrations authentication
python manage.py migrate

# 3. Ejecución de la suite completa de pruebas unitarias
python manage.py test
```

---

## 4. Evidencia de Pruebas Exitosas
```text
Creating test database for alias 'default'...
....................Found 20 test(s).
System check identified no issues (0 silenced).

----------------------------------------------------------------------
Ran 20 tests in 20.200s

OK
Destroying test database for alias 'default'...
```

**Pruebas unitarias ejecutadas con éxito (100% aprobadas):**
- Pruebas de Autenticación SSO y MFA (PSE-4): `test_login_success_retail`, `test_login_success_corporate_with_mfa`, `test_login_failed_missing_mfa`, `test_login_failed_invalid_credentials`.
- Pruebas de Roles y Permisos Granulares (PSE-26): `test_role_crud_and_keycloak_sync`, `test_granular_permission_assignment_and_unlinking`, `test_rbac_access_control_denied`, `test_roles_admin_ui_template`.
- Pruebas de Gestión de Clientes (PSE-2): `test_customer_registration_and_crud`, `test_customer_admin_ui_template`.
- Pruebas de Personas Jurídicas y Clasificación (PSE-3): `test_corporate_customer_registration_success`, `test_corporate_registration_weak_password`, `test_corporate_registration_duplicate_email`, `test_customer_classification_and_segmentation`, `test_corporate_customer_admin_ui_template`.
- Pruebas de Límites Transaccionales y Cumplimiento KYC (PSE-6):
  - `test_transaction_limit_parameterization`: Validación de configuración y actualización de límites por perfil.
  - `test_transaction_validation_success_and_kyc_alert`: Validación de transacción dentro de límites y generación automática de alerta KYC por alto valor (> 50M PYG).
  - `test_transaction_validation_limit_exceeded`: Validación de rechazo transaccional y generación de alerta `LIMIT_EXCEEDED` al superar el límite máximo.
  - `test_kyc_alert_status_update`: Validación de actualización de estado de alerta KYC (`REVIEWED` / `RESOLVED`).
  - `test_kyc_limits_admin_ui_template`: Validación de acceso a la plantilla web de límites y KYC (`kyc_limits_admin.html`).

---

## 5. Archivos Modificados / Creados
- `authentication/models.py`: Incorporación de modelos `TransactionLimit` y `KYCAlert` con docstrings en formato Google/Sphinx.
- `authentication/serializers.py`: Serializers `TransactionLimitSerializer` y `KYCAlertSerializer`.
- `authentication/views.py`: Vistas DRF y de plantilla (`TransactionLimitView`, `KYCAlertView`, `TransactionLimitValidationView`, `KYCLimitsAdminTemplateView`) documentadas con docstrings.
- `authentication/urls.py` y `globalexchange/urls.py`: Enrutamiento de endpoints y vistas de administración de límites y KYC.
- `authentication/templates/authentication/kyc_limits_admin.html`: Interfaz web interactiva en Bootstrap para parametrización de límites y gestión de alertas KYC.
- `authentication/migrations/0005_transactionlimit_kycalert.py`: Migración de base de datos.
- `authentication/tests.py`: Suite `KYCLimitsAndComplianceTests`.
- `docs/prompts/20260828_PSE-6_limites_kyc.md`: Registro CHIA obligatorio.
