# Global Exchange - Casa de Cambios (IS2 - FPUNA)

Sistema backend en Django y DRF para compra/venta de divisas, autenticación SSO/Keycloak (PSE-4) y gestión de roles y permisos (PSE-26).

## Instrucciones para Ejecutar en Otra Computadora

Si descargas el proyecto desde GitHub en otra computadora, sigue estos pasos para asegurar su correcto funcionamiento:

### 1. Clonar el Repositorio y Entrar al Directorio
```bash
git clone <url-del-repositorio>
cd Proyecto
```

### 2. Instalar las Dependencias
Crea y activa un entorno virtual (recomendado) e instala las librerías necesarias:
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
```

### 3. Aplicar las Migraciones de Base de Datos
```bash
python manage.py migrate
```

### 4. Cargar Datos de Prueba (Usuarios y Permisos)
Ejecuta el script de configuración para poblar los usuarios de prueba y los permisos del sistema (PSE-26):
```bash
python setup_test_data.py
```

### 5. Ejecutar la Suite de Pruebas Unitarias
Para confirmar que todo el código pasa las pruebas correctamente (100% éxito):
```bash
python manage.py test
```

### 6. Iniciar el Servidor de Desarrollo
```bash
python manage.py runserver
```

### Credenciales de Acceso:
- **Administrador:** `admin` / `password123` (Acceso completo a gestión de roles en `/roles/admin/`)
- **Cliente Minorista:** `cliente_minorista` / `password123`
- **Cliente Corporativo:** `cliente_corporativo` / `password123` (Requiere iToken/MFA `123456`)
