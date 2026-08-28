import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog, UserProfile


class KeycloakSSOLoginView(APIView):
    """
    API view handling Single Sign-On (SSO) authentication and MFA/iToken validation via Keycloak standards.
    
    Methods:
        post(request): Authenticates user credentials, verifies MFA if required, 
                       issues a JWT token, and logs audit events.
    """
    
    def post(self, request):
        """
        Processes login request, validating username, password, and MFA code when applicable.
        
        Args:
            request (Request): HTTP request containing username, password, and optional mfa_token.
            
        Returns:
            Response: JSON response containing JWT access token and user role dashboard options, 
                      or error details with audit logging upon failure.
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

        # Check user profile and MFA requirement
        profile, created = UserProfile.objects.get_or_create(user=user)

        if profile.mfa_required:
            if not mfa_token or mfa_token != '123456':  # Standard mock iToken/MFA check
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

        # Successful authentication & SSO simulation
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
                'historial': '/api/exchange/history/'
            }
        }, status=status.HTTP_200_OK)


class DashboardView(APIView):
    """
    API view providing access to the personalized user dashboard upon successful authentication.
    
    Methods:
        get(request): Returns dashboard navigation and options according to user role.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves personalized dashboard options based on the authenticated user's role.
        
        Args:
            request (Request): Authenticated HTTP request.
            
        Returns:
            Response: JSON response with allowed panel options (simulate, operate, history).
        """
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        return Response({
            'username': user.username,
            'role': profile.role,
            'available_options': [
                {'name': 'Simular Transacción', 'endpoint': '/api/exchange/simulate/'},
                {'name': 'Operar Compra/Venta', 'endpoint': '/api/exchange/operate/'},
                {'name': 'Ver Historial', 'endpoint': '/api/exchange/history/'},
            ]
        }, status=status.HTTP_200_OK)
