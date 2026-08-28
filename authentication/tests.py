from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserProfile, AuditLog


class AuthenticationTests(TestCase):
    """
    Test suite for Keycloak SSO Authentication, MFA verification, role-based dashboards, 
    and audit logging in Global Exchange (PSE-4).
    
    Methods:
        setUp(): Initializes test users (retail client, corporate client, admin) and profiles.
        test_login_success_retail(): Tests successful login for retail client without MFA.
        test_login_success_corporate_with_mfa(): Tests successful login for corporate client with valid MFA/iToken.
        test_login_failed_missing_mfa(): Tests login failure when MFA is required but missing or invalid.
        test_login_failed_invalid_credentials(): Tests login failure and audit logging for incorrect credentials.
    """

    def setUp(self):
        """
        Sets up test database records including users with different roles and MFA configurations.
        """
        # Retail user (no mandatory MFA)
        self.retail_user = User.objects.create_user(username='retail_user', password='password123')
        self.retail_profile, _ = UserProfile.objects.get_or_create(user=self.retail_user, role='RETAIL_CLIENT')

        # Corporate user (mandatory MFA)
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

        # Verify audit log was created
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

        # Verify audit log
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

        # Verify audit log for MFA failure
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

        # Verify audit log for failed login
        log_entry = AuditLog.objects.filter(user_identifier='retail_user', action='LOGIN_FAILED').first()
        self.assertIsNotNone(log_entry)
        self.assertIn('Credenciales inválidas', log_entry.details)
