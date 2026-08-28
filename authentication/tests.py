from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserProfile, AuditLog, Role, SystemPermission


class AuthenticationTests(TestCase):
    """
    Test suite for Keycloak SSO Authentication, MFA verification, role-based dashboards, 
    and audit logging in Global Exchange (PSE-4).
    """

    def setUp(self):
        """
        Sets up test database records including users with different roles and MFA configurations.
        """
        self.retail_user = User.objects.create_user(username='retail_user', password='password123')
        self.retail_profile, _ = UserProfile.objects.get_or_create(user=self.retail_user, role='RETAIL_CLIENT')

        self.corp_user = User.objects.create_user(username='corp_user', password='password123')
        self.corp_profile, _ = UserProfile.objects.get_or_create(user=self.corp_user, role='CORPORATE_CLIENT')

        self.client = APIClient()

    def test_login_success_retail(self):
        """
        Tests that a retail user can log in successfully via SSO without MFA, receiving a JWT token and dashboard options.
        """
        response = self.client.post('/api/auth/login/', {
            'username': 'retail_user',
            'password': 'password123'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertEqual(response.data['user']['role'], 'RETAIL_CLIENT')
        self.assertFalse(response.data['user']['mfa_required'])

        log_entry = AuditLog.objects.filter(user_identifier='retail_user', action='LOGIN_SUCCESS').first()
        self.assertIsNotNone(log_entry)

    def test_login_success_corporate_with_mfa(self):
        """
        Tests that a corporate user logging in with correct credentials and valid MFA token (123456) succeeds.
        """
        response = self.client.post('/api/auth/login/', {
            'username': 'corp_user',
            'password': 'password123',
            'mfa_token': '123456'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertEqual(response.data['user']['role'], 'CORPORATE_CLIENT')
        self.assertTrue(response.data['user']['mfa_required'])

        log_entry = AuditLog.objects.filter(user_identifier='corp_user', action='LOGIN_SUCCESS').first()
        self.assertIsNotNone(log_entry)

    def test_login_failed_missing_mfa(self):
        """
        Tests that a corporate user attempting to log in without the required MFA token receives 403 Forbidden and audit log.
        """
        response = self.client.post('/api/auth/login/', {
            'username': 'corp_user',
            'password': 'password123'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)

        log_entry = AuditLog.objects.filter(user_identifier='corp_user', action='LOGIN_FAILED_MFA').first()
        self.assertIsNotNone(log_entry)

    def test_login_failed_invalid_credentials(self):
        """
        Tests that incorrect credentials result in 401 Unauthorized and a corresponding security audit log entry.
        """
        response = self.client.post('/api/auth/login/', {
            'username': 'retail_user',
            'password': 'wrongpassword'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

        log_entry = AuditLog.objects.filter(user_identifier='retail_user', action='LOGIN_FAILED').first()
        self.assertIsNotNone(log_entry)
        self.assertIn('Credenciales inválidas', log_entry.details)


class RolePermissionManagementTests(TestCase):
    """
    Test suite for Role and Permission Management, RBAC validation, Keycloak synchronization,
    and audit logging (PSE-26).
    """

    def setUp(self):
        """
        Sets up admin user, regular user, system permissions, and test client.
        """
        self.admin_user = User.objects.create_user(username='admin_user', password='password123', is_staff=True)
        self.admin_profile, _ = UserProfile.objects.get_or_create(user=self.admin_user, role='ADMIN')

        self.regular_user = User.objects.create_user(username='regular_user', password='password123')
        self.regular_profile, _ = UserProfile.objects.get_or_create(user=self.regular_user, role='RETAIL_CLIENT')

        self.perm1 = SystemPermission.objects.create(code='MANAGE_ROLES', name='Gestionar Roles', description='Crear y editar roles')
        self.perm2 = SystemPermission.objects.create(code='OPERATE_EXCHANGE', name='Operar Divisas', description='Comprar y vender divisas')

        self.client = APIClient()

    def test_role_crud_and_keycloak_sync(self):
        """
        Tests creating, listing, modifying, and deactivating roles with Keycloak synchronization and audit logging (Criteria 1, 3, 5).
        """
        self.client.force_authenticate(user=self.admin_user)

        # 1. Create Role
        response = self.client.post('/api/roles/', {
            'name': 'Analista de Riesgo',
            'description': 'Rol para análisis de riesgo cambiario',
            'permission_ids': [self.perm1.id]
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        role_id = response.data['id']
        self.assertTrue(response.data['keycloak_synced'])

        # Verify Audit Log
        log_create = AuditLog.objects.filter(user_identifier='admin_user', action='ROLE_CREATED').first()
        self.assertIsNotNone(log_create)

        # 2. List Roles
        response_list = self.client.get('/api/roles/')
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response_list.data), 1)

        # 3. Modify Role (PUT)
        response_update = self.client.put(f'/api/roles/{role_id}/', {
            'name': 'Analista Senior de Riesgo',
            'description': 'Descripción actualizada'
        }, format='json')
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)
        self.assertEqual(response_update.data['name'], 'Analista Senior de Riesgo')
        self.assertTrue(response_update.data['keycloak_synced'])

        log_update = AuditLog.objects.filter(user_identifier='admin_user', action='ROLE_UPDATED').first()
        self.assertIsNotNone(log_update)

        # 4. Deactivate Role (DELETE / soft delete)
        response_delete = self.client.delete(f'/api/roles/{role_id}/')
        self.assertEqual(response_delete.status_code, status.HTTP_200_OK)

        log_deactivate = AuditLog.objects.filter(user_identifier='admin_user', action='ROLE_DEACTIVATED').first()
        self.assertIsNotNone(log_deactivate)

    def test_granular_permission_assignment_and_unlinking(self):
        """
        Tests assigning and unlinking granular permissions to a role (Criterion 2).
        """
        self.client.force_authenticate(user=self.admin_user)
        role = Role.objects.create(name='Operador', description='Operador cambiario')

        # Assign permission
        res_assign = self.client.post(f'/api/roles/{role.id}/permissions/', {
            'permission_ids': [self.perm2.id]
        }, format='json')
        self.assertEqual(res_assign.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_assign.data['permissions']), 1)

        log_assign = AuditLog.objects.filter(user_identifier='admin_user', action='ROLE_PERMISSION_ASSIGNED').first()
        self.assertIsNotNone(log_assign)

        # Unlink permission
        res_unlink = self.client.delete(f'/api/roles/{role.id}/permissions/', {
            'permission_ids': [self.perm2.id]
        }, format='json')
        self.assertEqual(res_unlink.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_unlink.data['permissions']), 0)

        log_unlink = AuditLog.objects.filter(user_identifier='admin_user', action='ROLE_PERMISSION_UNLINKED').first()
        self.assertIsNotNone(log_unlink)

    def test_rbac_access_control_denied(self):
        """
        Tests that non-admin users cannot access role management endpoints (Criterion 4).
        """
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get('/api/roles/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response_post = self.client.post('/api/roles/', {'name': 'Hacker Role'}, format='json')
        self.assertEqual(response_post.status_code, status.HTTP_403_FORBIDDEN)

    def test_roles_admin_ui_template(self):
        """
        Tests that admin user can access the HTML admin GUI view for roles and permissions.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/roles/admin/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'authentication/roles_admin.html')
