from django.db import models
from django.contrib.auth.models import User

class AuditLog(models.Model):
    """
    Model representing security and authentication audit logs.
    
    Attributes:
        user_identifier (str): Username or email used in the attempt.
        action (str): Description of the action (e.g., 'LOGIN_SUCCESS', 'ROLE_CREATED').
        ip_address (str): IP address of the client.
        timestamp (datetime): Exact date and time of the event.
        details (str): Additional context or error details.
    """
    user_identifier = models.CharField(max_length=255)
    action = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        """
        Returns a string representation of the audit log entry.
        
        Returns:
            str: Formatted string with timestamp, action, and user identifier.
        """
        return f"[{self.timestamp}] {self.action} - {self.user_identifier}"


class SystemPermission(models.Model):
    """
    Model representing granular permissions in Global Exchange system (PSE-26).
    
    Attributes:
        code (str): Unique system code for the permission (e.g., 'MANAGE_ROLES').
        name (str): Human-readable permission name.
        description (str): Detailed description of what the permission allows.
    """
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        """
        Returns string representation of permission.
        
        Returns:
            str: Permission name and code.
        """
        return f"{self.name} ({self.code})"


class Role(models.Model):
    """
    Model representing user roles with granular permissions and Keycloak synchronization (PSE-26).
    
    Attributes:
        name (str): Unique role name (e.g., 'ADMINISTRADOR', 'ANALISTA_CAMBIARIO').
        description (str): Role description.
        permissions (ManyToManyField): Granular permissions assigned to this role.
        is_active (bool): Whether the role is active or deactivated.
        keycloak_synced (bool): Flag indicating synchronization status with Keycloak policies.
        created_at (datetime): Timestamp when the role was created.
        updated_at (datetime): Timestamp when the role was last updated.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    permissions = models.ManyToManyField(SystemPermission, related_name='roles', blank=True)
    is_active = models.BooleanField(default=True)
    keycloak_synced = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Returns string representation of role.
        
        Returns:
            str: Role name and status.
        """
        status = "Activo" if self.is_active else "Inactivo"
        return f"{self.name} [{status}]"


class UserProfile(models.Model):
    """
    Extended user profile supporting roles and MFA requirements for Global Exchange.
    
    Attributes:
        user (User): Associated Django auth user.
        role (str): Assigned role (e.g., 'ADMIN', 'CORPORATE_CLIENT', 'RETAIL_CLIENT').
        role_ref (Role): Optional ForeignKey reference to dynamic Role model.
        mfa_required (bool): Whether Multi-Factor Authentication / iToken is strictly required.
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('CORPORATE_CLIENT', 'Cliente Corporativo'),
        ('RETAIL_CLIENT', 'Cliente Minorista'),
        ('EXCHANGE_ANALYST', 'Analista Cambiario'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='RETAIL_CLIENT')
    role_ref = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    mfa_required = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Overrides save to automatically enforce MFA for admin and corporate roles.
        """
        if self.role in ['ADMIN', 'CORPORATE_CLIENT']:
            self.mfa_required = True
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a string representation of the user profile.
        
        Returns:
            str: Username and role.
        """
        return f"{self.user.username} ({self.role})"


class Customer(models.Model):
    """
    Model representing bank customers with segmentation and profile management (PSE-2, PSE-3).
    
    Attributes:
        first_name (str): Customer's first name.
        last_name (str): Customer's last name.
        document_number (str): Unique identification number (CI or RUC).
        company_name (str): Company name for legal entities (Persona Jurídica - PSE-3).
        ruc (str): RUC for legal entities (PSE-3).
        client_type (str): Segmentation category ('RETAIL', 'CORPORATE', 'VIP').
        email (str): Unique contact email address.
        phone (str): Contact phone number.
        address (str): Physical address.
        is_active (bool): Whether the customer profile is active.
        keycloak_synced (bool): Whether account is synced with Keycloak IdP (PSE-3).
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last modification timestamp.
    """
    CLIENT_TYPE_CHOICES = [
        ('RETAIL', 'Cliente Minorista'),
        ('CORPORATE', 'Cliente Corporativo'),
        ('VIP', 'Cliente VIP'),
    ]

    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    document_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    ruc = models.CharField(max_length=50, blank=True, null=True, unique=True)
    client_type = models.CharField(max_length=50, choices=CLIENT_TYPE_CHOICES, default='RETAIL')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    keycloak_synced = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Returns string representation of the customer.
        
        Returns:
            str: Full name or company name, document/RUC, and client type.
        """
        name = self.company_name or f"{self.first_name or ''} {self.last_name or ''}".strip()
        doc = self.ruc or self.document_number or 'N/A'
        return f"{name} ({doc}) - {self.client_type}"
