from django.db import models
from django.contrib.auth.models import User

class AuditLog(models.Model):
    """
    Model representing security and authentication audit logs.
    
    Attributes:
        user_identifier (str): Username or email used in the attempt.
        action (str): Description of the action (e.g., 'LOGIN_SUCCESS', 'LOGIN_FAILED').
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


class UserProfile(models.Model):
    """
    Extended user profile supporting roles and MFA requirements for Global Exchange.
    
    Attributes:
        user (User): Associated Django auth user.
        role (str): Assigned role (e.g., 'ADMIN', 'CORPORATE_CLIENT', 'RETAIL_CLIENT').
        mfa_required (bool): Whether Multi-Factor Authentication / iToken is strictly required.
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('CORPORATE_CLIENT', 'Cliente Corporativo'),
        ('RETAIL_CLIENT', 'Cliente Minorista'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='RETAIL_CLIENT')
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
