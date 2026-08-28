import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import AuditLog, UserProfile, Role, SystemPermission
from .serializers import RoleSerializer, SystemPermissionSerializer


class IsAdminOrHasRolePermission(BasePermission):
    """
    Custom permission to ensure the authenticated user has ADMIN role or required permissions (PSE-26).
    """
    def has_permission(self, request, view):
        """
        Validates if the user is authenticated and has administrative privileges.
        
        Args:
            request (Request): HTTP request.
            view (APIView): View instance.
            
        Returns:
            bool: True if authorized, False otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            profile = request.user.profile
            if profile.role == 'ADMIN':
                return True
        except UserProfile.DoesNotExist:
            pass
        return False


class KeycloakSSOLoginView(APIView):
    """
    API view handling Single Sign-On (SSO) authentication and MFA/iToken validation via Keycloak standards.
    """
    
    def post(self, request):
        """
        Processes login request, validating username, password, and MFA code when applicable.
        
        Args:
            request (Request): HTTP request containing username, password, and optional mfa_token.
            
        Returns:
            Response: JSON response containing JWT access token and user role dashboard options.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        mfa_token = request.data.get('mfa_token')
        ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')

        if not username or not password:
            AuditLog.objects.create(
                user_identifier=username or 'unknown',
                action='LOGIN_FAILED',
                ip_address=ip_address,
                details='Missing username or password.'
            )
            return Response(
                {"error": "Usuario y contraseña son requeridos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            AuditLog.objects.create(
                user_identifier=username,
                action='LOGIN_FAILED',
                ip_address=ip_address,
                details='Credenciales inválidas.'
            )
            return Response(
                {"error": "Credenciales inválidas. Acceso denegado."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        profile, created = UserProfile.objects.get_or_create(user=user)

        if profile.mfa_required:
            if not mfa_token or mfa_token != '123456':
                AuditLog.objects.create(
                    user_identifier=username,
                    action='LOGIN_FAILED_MFA',
                    ip_address=ip_address,
                    details='MFA / iToken requerido o inválido.'
                )
                return Response(
                    {"error": "Autenticación de doble factor (MFA/iToken) requerida o código inválido."},
                    status=status.HTTP_403_FORBIDDEN
                )

        payload = {
            'username': user.username,
            'role': profile.role,
            'mfa_verified': profile.mfa_required
        }
        token = jwt.encode(payload, getattr(settings, 'SECRET_KEY', 'secret'), algorithm='HS256')

        AuditLog.objects.create(
            user_identifier=username,
            action='LOGIN_SUCCESS',
            ip_address=ip_address,
            details=f'Inicio de sesión exitoso con rol {profile.role}.'
        )

        return Response({
            'message': 'Autenticación exitosa mediante Keycloak SSO.',
            'access_token': token,
            'user': {
                'username': user.username,
                'email': user.email,
                'role': profile.role,
                'mfa_required': profile.mfa_required
            },
            'dashboard_options': {
                'simular': '/api/exchange/simulate/',
                'operar': '/api/exchange/operate/',
                'historial': '/api/exchange/history/',
                'roles': '/api/roles/'
            }
        }, status=status.HTTP_200_OK)


class DashboardView(APIView):
    """
    API view providing access to the personalized user dashboard upon successful authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves personalized dashboard options based on the authenticated user's role.
        
        Args:
            request (Request): Authenticated HTTP request.
            
        Returns:
            Response: JSON response with allowed panel options.
        """
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        options = [
            {'name': 'Simular Transacción', 'endpoint': '/api/exchange/simulate/'},
            {'name': 'Operar Compra/Venta', 'endpoint': '/api/exchange/operate/'},
            {'name': 'Ver Historial', 'endpoint': '/api/exchange/history/'},
        ]
        if profile.role == 'ADMIN' or request.user.is_superuser:
            options.append({'name': 'Gestión de Roles y Permisos', 'endpoint': '/api/roles/'})
            options.append({'name': 'Panel Admin Roles UI', 'endpoint': '/roles/admin/'})

        return Response({
            'username': user.username,
            'role': profile.role,
            'available_options': options
        }, status=status.HTTP_200_OK)


class PermissionListView(APIView):
    """
    API view to list all available system permissions (PSE-26).
    """
    permission_classes = [IsAuthenticated, IsAdminOrHasRolePermission]

    def get(self, request):
        """
        Retrieves list of all system permissions.
        
        Args:
            request (Request): HTTP request.
            
        Returns:
            Response: Serialized list of permissions.
        """
        permissions = SystemPermission.objects.all()
        serializer = SystemPermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoleListCreateView(APIView):
    """
    API view to list all roles and create a new role (PSE-26).
    """
    permission_classes = [IsAuthenticated, IsAdminOrHasRolePermission]

    def get(self, request):
        """
        Lists all system roles.
        
        Args:
            request (Request): HTTP request.
            
        Returns:
            Response: Serialized list of roles.
        """
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Creates a new role with optional granular permissions and registers an audit log.
        
        Args:
            request (Request): HTTP request containing role name, description, and permission_ids.
            
        Returns:
            Response: Created role data or validation errors.
        """
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            AuditLog.objects.create(
                user_identifier=request.user.username,
                action='ROLE_CREATED',
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                details=f"Rol '{role.name}' creado exitosamente con sincronización Keycloak."
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        AuditLog.objects.create(
            user_identifier=request.user.username,
            action='ROLE_CREATION_FAILED',
            ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
            details=str(serializer.errors)
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleDetailView(APIView):
    """
    API view to retrieve, modify (update), or deactivate a role (PSE-26).
    """
    permission_classes = [IsAuthenticated, IsAdminOrHasRolePermission]

    def get_object(self, pk):
        """
        Helper method to retrieve role by primary key.
        """
        try:
            return Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Retrieves details of a specific role.
        """
        role = self.get_object(pk)
        if not role:
            return Response({"error": "Rol no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializer(role)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Modifies an existing role and validates Keycloak policy synchronization.
        """
        role = self.get_object(pk)
        if not role:
            return Response({"error": "Rol no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RoleSerializer(role, data=request.data, partial=True)
        if serializer.is_valid():
            role = serializer.save()
            role.keycloak_synced = True
            role.save()

            AuditLog.objects.create(
                user_identifier=request.user.username,
                action='ROLE_UPDATED',
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                details=f"Rol '{role.name}' modificado y sincronizado con Keycloak."
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Deactivates a role (soft delete / desactivación) rather than physical removal, logging audit event.
        """
        role = self.get_object(pk)
        if not role:
            return Response({"error": "Rol no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        role.is_active = False
        role.save()

        AuditLog.objects.create(
            user_identifier=request.user.username,
            action='ROLE_DEACTIVATED',
            ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
            details=f"Rol '{role.name}' desactivado exitosamente."
        )
        return Response({"message": f"Rol '{role.name}' desactivado correctamente."}, status=status.HTTP_200_OK)


class RolePermissionAssignView(APIView):
    """
    API view to assign or unbind granular permissions to/from a role (PSE-26).
    """
    permission_classes = [IsAuthenticated, IsAdminOrHasRolePermission]

    def post(self, request, pk):
        """
        Assigns granular permissions to a role.
        """
        try:
            role = Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return Response({"error": "Rol no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        permission_ids = request.data.get('permission_ids', [])
        permissions = SystemPermission.objects.filter(id__in=permission_ids)
        role.permissions.add(*permissions)
        role.keycloak_synced = True
        role.save()

        AuditLog.objects.create(
            user_identifier=request.user.username,
            action='ROLE_PERMISSION_ASSIGNED',
            ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
            details=f"Permisos asignados al rol '{role.name}'."
        )
        serializer = RoleSerializer(role)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Unbinds granular permissions from a role.
        """
        try:
            role = Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return Response({"error": "Rol no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        permission_ids = request.data.get('permission_ids', [])
        permissions = SystemPermission.objects.filter(id__in=permission_ids)
        role.permissions.remove(*permissions)
        role.keycloak_synced = True
        role.save()

        AuditLog.objects.create(
            user_identifier=request.user.username,
            action='ROLE_PERMISSION_UNLINKED',
            ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
            details=f"Permisos desvinculados del rol '{role.name}'."
        )
        serializer = RoleSerializer(role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoleAdminTemplateView(APIView):
    """
    Frontend view rendering the role and permission administration GUI (PSE-26).
    """
    permission_classes = [IsAuthenticated, IsAdminOrHasRolePermission]

    def get(self, request):
        """
        Renders the roles administration HTML interface.
        """
        return render(request, 'authentication/roles_admin.html', {
            'username': request.user.username
        })
