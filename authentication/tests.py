from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserProfile, AuditLog, Role, SystemPermission, Customer, TransactionLimit, KYCAlert, ClientDocument


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


class CustomerManagementTests(TestCase):
    """
    Test suite for Customer Registration, Profile Management, Segmentation, and Audit Logging (PSE-2).
    """

    def setUp(self):
        """
        Sets up admin user, regular user, and test client.
        """
        self.admin_user = User.objects.create_user(username='admin_customer', password='password123', is_staff=True)
        self.admin_profile, _ = UserProfile.objects.get_or_create(user=self.admin_user, role='ADMIN')

        self.client = APIClient()

    def test_customer_registration_and_crud(self):
        """
        Tests customer registration, listing with segmentation, profile update, and deactivation (PSE-2).
        """
        self.client.force_authenticate(user=self.admin_user)

        # 1. Register Customer (POST)
        response = self.client.post('/api/customers/', {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'document_number': '1234567-1',
            'client_type': 'VIP',
            'email': 'juan.perez@example.com',
            'phone': '0981123456',
            'address': 'Asunción, Paraguay'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        customer_id = response.data['id']
        self.assertEqual(response.data['client_type'], 'VIP')
        self.assertTrue(response.data['is_active'])

        # Verify Audit Log
        log_create = AuditLog.objects.filter(user_identifier='admin_customer', action='CUSTOMER_CREATED').first()
        self.assertIsNotNone(log_create)

        # 2. List Customers and filter by client_type
        response_list = self.client.get('/api/customers/?client_type=VIP')
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list.data), 1)

        # 3. Update Customer Profile (PUT)
        response_update = self.client.put(f'/api/customers/{customer_id}/', {
            'phone': '0982999888'
        }, format='json')
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)
        self.assertEqual(response_update.data['phone'], '0982999888')

        log_update = AuditLog.objects.filter(user_identifier='admin_customer', action='CUSTOMER_UPDATED').first()
        self.assertIsNotNone(log_update)

        # 4. Deactivate Customer (DELETE / soft delete)
        response_delete = self.client.delete(f'/api/customers/{customer_id}/')
        self.assertEqual(response_delete.status_code, status.HTTP_200_OK)

        log_deactivate = AuditLog.objects.filter(user_identifier='admin_customer', action='CUSTOMER_DEACTIVATED').first()
        self.assertIsNotNone(log_deactivate)

    def test_customer_admin_ui_template(self):
        """
        Tests that admin user can access the HTML template view for customer administration.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/customers/admin/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'authentication/customer_admin.html')


class CorporateCustomerSegmentationTests(TestCase):
    """
    Test suite for Corporate Customer Registration (Personas Jurídicas) and Classification/Segmentation (PSE-3).
    """

    def setUp(self):
        """
        Sets up admin user and test client.
        """
        self.admin_user = User.objects.create_user(username='admin_pse3', password='password123', is_staff=True)
        self.admin_profile, _ = UserProfile.objects.get_or_create(user=self.admin_user, role='ADMIN')
        self.client = APIClient()

    def test_corporate_customer_registration_success(self):
        """
        Tests successful corporate customer registration with RUC, strong password, and Keycloak delegation.
        """
        response = self.client.post('/api/corporate-customers/register/', {
            'company_name': 'Global Solutions S.A.',
            'ruc': '80098765-1',
            'email': 'contacto@globalsolutions.com.py',
            'password': 'SecurePassword123!',
            'phone': '021456789',
            'address': 'Asunción, Paraguay'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer']['client_type'], 'CORPORATE')
        self.assertTrue(response.data['customer']['keycloak_synced'])

        log_entry = AuditLog.objects.filter(action='CORPORATE_CUSTOMER_REGISTERED').first()
        self.assertIsNotNone(log_entry)

    def test_corporate_registration_weak_password(self):
        """
        Tests that corporate registration fails when password does not meet security requirements.
        """
        response = self.client.post('/api/corporate-customers/register/', {
            'company_name': 'Weak Pass S.A.',
            'ruc': '80011122-3',
            'email': 'test@weak.com',
            'password': 'weak'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_corporate_registration_duplicate_email(self):
        """
        Tests that corporate registration is denied if email is already registered.
        """
        # Register first
        self.client.post('/api/corporate-customers/register/', {
            'company_name': 'Company A',
            'ruc': '80011111-1',
            'email': 'duplicado@empresa.com',
            'password': 'SecurePassword123!'
        }, format='json')

        # Try duplicate email
        response = self.client.post('/api/corporate-customers/register/', {
            'company_name': 'Company B',
            'ruc': '80022222-2',
            'email': 'duplicado@empresa.com',
            'password': 'SecurePassword123!'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_customer_classification_and_segmentation(self):
        """
        Tests viewing customer segmentation summary and reclassifying customer categories.
        """
        self.client.force_authenticate(user=self.admin_user)

        # Create a customer
        reg_res = self.client.post('/api/corporate-customers/register/', {
            'company_name': 'Segment Test S.A.',
            'ruc': '80055544-0',
            'email': 'segment@test.com',
            'password': 'SecurePassword123!'
        }, format='json')
        cust_id = reg_res.data['customer']['id']

        # Get classification summary
        get_res = self.client.get('/api/customers/classification/')
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data['segmentation_summary']['corporate_count'], 1)

        # Reclassify customer to VIP
        post_res = self.client.post('/api/customers/classification/', {
            'customer_id': cust_id,
            'client_type': 'VIP'
        }, format='json')
        self.assertEqual(post_res.status_code, status.HTTP_200_OK)
        self.assertEqual(post_res.data['customer']['client_type'], 'VIP')

        log_reclass = AuditLog.objects.filter(action='CUSTOMER_RECLASSIFIED').first()
        self.assertIsNotNone(log_reclass)

    def test_corporate_customer_admin_ui_template(self):
        """
        Tests that admin user can access the HTML template view for corporate customer admin.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/customers/corporate/admin/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'authentication/corporate_customer_admin.html')


class KYCLimitsAndComplianceTests(TestCase):
    """
    Test suite for Transaction Limit Validation, KYC Compliance Alerts, and Parameterization (PSE-6).
    """

    def setUp(self):
        """
        Sets up admin user, customer, and test client.
        """
        self.admin_user = User.objects.create_user(username='admin_kyc', password='password123', is_staff=True)
        self.admin_profile, _ = UserProfile.objects.get_or_create(user=self.admin_user, role='ADMIN')

        self.customer = Customer.objects.create(
            first_name='María',
            last_name='González',
            document_number='3456789-2',
            client_type='VIP',
            email='maria.gonzalez@example.com'
        )
        self.client = APIClient()

    def test_transaction_limit_parameterization(self):
        """
        Tests parameterizing transaction limits for a client type (PSE-6).
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/limits/', {
            'client_type': 'VIP',
            'min_amount': '100000.00',
            'max_amount': '2000000000.00',
            'daily_limit': '10000000000.00'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['max_amount']), 2000000000.00)

        log_entry = AuditLog.objects.filter(action='TRANSACTION_LIMIT_UPDATED').first()
        self.assertIsNotNone(log_entry)

    def test_transaction_validation_success_and_kyc_alert(self):
        """
        Tests transaction validation within limits and automatic high-value KYC alert generation (> 50M PYG).
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/transactions/validate-limit/', {
            'customer_id': self.customer.id,
            'amount': 75000000.00  # 75 Million PYG (> 50M threshold)
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['kyc_alert_generated'])

        # Verify KYC Alert created in DB
        alert = KYCAlert.objects.filter(customer=self.customer, alert_type='HIGH_VALUE_TRANSACTION').first()
        self.assertIsNotNone(alert)
        self.assertEqual(alert.status, 'PENDING')

    def test_transaction_validation_limit_exceeded(self):
        """
        Tests transaction rejection and LIMIT_EXCEEDED KYC alert when amount exceeds max limit.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/transactions/validate-limit/', {
            'customer_id': self.customer.id,
            'amount': 2000000000.00  # 2 Billion PYG (> default 1B max limit)
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

        alert = KYCAlert.objects.filter(customer=self.customer, alert_type='LIMIT_EXCEEDED').first()
        self.assertIsNotNone(alert)

    def test_kyc_alert_status_update(self):
        """
        Tests updating KYC alert status (e.g. marking as REVIEWED or RESOLVED).
        """
        self.client.force_authenticate(user=self.admin_user)
        alert = KYCAlert.objects.create(
            customer=self.customer,
            alert_type='HIGH_VALUE_TRANSACTION',
            amount=60000000.00,
            status='PENDING'
        )

        response = self.client.patch(f'/api/kyc-alerts/{alert.id}/', {
            'status': 'RESOLVED'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'RESOLVED')

        log_entry = AuditLog.objects.filter(action='KYC_ALERT_UPDATED').first()
        self.assertIsNotNone(log_entry)

    def test_kyc_limits_admin_ui_template(self):
        """
        Tests that admin user can access the HTML template view for KYC limits and alerts admin.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/limits/kyc/admin/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'authentication/kyc_limits_admin.html')


class UserMenuNavigationTests(TestCase):
    """
    Test suite for Main Menu Structure and Dynamic Navigation based on user role and permissions (PSE-28).
    """

    def setUp(self):
        """
        Sets up admin user, corporate user, retail user, and test client.
        """
        self.admin_user = User.objects.create_user(username='admin_menu', password='password123', is_staff=True)
        self.admin_profile, _ = UserProfile.objects.get_or_create(user=self.admin_user, role='ADMIN')

        self.corp_user = User.objects.create_user(username='corp_menu', password='password123')
        self.corp_profile, _ = UserProfile.objects.get_or_create(user=self.corp_user, role='CORPORATE_CLIENT')

        self.client = APIClient()

    def test_user_menu_api_admin(self):
        """
        Tests that the menu API returns administrative modules for an admin user (PSE-28).
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/menu/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'ADMIN')
        
        # Verify admin menu items exist
        menu_items = response.data['menu_items']
        urls = [item['url'] for item in menu_items]
        self.assertIn('/roles/admin/', urls)
        self.assertIn('/customers/admin/', urls)
        self.assertIn('/limits/kyc/admin/', urls)

    def test_user_menu_api_corporate(self):
        """
        Tests that the menu API returns corporate modules for a corporate client user (PSE-28).
        """
        self.client.force_authenticate(user=self.corp_user)
        response = self.client.get('/api/menu/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'CORPORATE_CLIENT')

        menu_items = response.data['menu_items']
        urls = [item['url'] for item in menu_items]
        self.assertIn('/customers/corporate/admin/', urls)

    def test_main_menu_template_view(self):
        """
        Tests that authenticated user can access the main menu template view successfully.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/menu/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'authentication/main_menu.html')


class ClientDocumentManagementTests(TestCase):
    """
    Test suite for Digital Client Documentation Management and KYC Audit (PSE-7).
    """

    def setUp(self):
        """
        Sets up admin user, customer, and test client.
        """
        self.admin_user = User.objects.create_user(username='admin_docs', password='password123', is_staff=True)
        self.admin_profile, _ = UserProfile.objects.get_or_create(user=self.admin_user, role='ADMIN')

        self.customer = Customer.objects.create(
            first_name='Carlos',
            last_name='Benítez',
            document_number='4567891-3',
            client_type='VIP',
            email='carlos.benitez@example.com'
        )
        self.client = APIClient()

    def test_client_document_upload_and_list(self):
        """
        Tests uploading a digitalized client document and listing documents (PSE-7).
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/documents/', {
            'customer': self.customer.id,
            'document_type': 'CI_FRONT',
            'file_name': 'cedula_carlos.pdf',
            'file_url': '/media/docs/cedula_carlos.pdf'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'PENDING')
        doc_id = response.data['id']

        log_upload = AuditLog.objects.filter(action='CLIENT_DOCUMENT_UPLOADED').first()
        self.assertIsNotNone(log_upload)

        # List documents
        res_list = self.client.get('/api/documents/')
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res_list.data), 1)

    def test_client_document_audit_verification(self):
        """
        Tests auditing and updating document verification status to VERIFIED (PSE-7).
        """
        self.client.force_authenticate(user=self.admin_user)
        doc = ClientDocument.objects.create(
            customer=self.customer,
            document_type='INCOME_PROOF',
            file_name='comprobante.pdf',
            status='PENDING'
        )

        response = self.client.patch(f'/api/documents/{doc.id}/', {
            'status': 'VERIFIED'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'VERIFIED')

        log_audit = AuditLog.objects.filter(action='CLIENT_DOCUMENT_AUDITED').first()
        self.assertIsNotNone(log_audit)

    def test_client_documents_admin_ui_template(self):
        """
        Tests that admin user can access the client documents administration HTML template view.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/documents/admin/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'authentication/client_documents_admin.html')

    def test_menu_includes_documents_module(self):
        """
        Tests that the dynamic menu API includes the document management module for admin users.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/menu/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        urls = [item['url'] for item in response.data['menu_items']]
        self.assertIn('/documents/admin/', urls)
