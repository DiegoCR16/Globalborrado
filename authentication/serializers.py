from rest_framework import serializers
from .models import Role, SystemPermission, Customer

class SystemPermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for SystemPermission model.
    
    Attributes:
        id (int): Permission ID.
        code (str): Unique permission code.
        name (str): Permission name.
        description (str): Description.
    """
    class Meta:
        model = SystemPermission
        fields = ['id', 'code', 'name', 'description']


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role model with support for reading and writing granular permissions.
    
    Attributes:
        permissions (SystemPermissionSerializer): Read-only nested permissions.
        permission_ids (PrimaryKeyRelatedField): Write-only list of permission IDs.
    """
    permissions = SystemPermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=SystemPermission.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='permissions'
    )

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'permissions', 'permission_ids',
            'is_active', 'keycloak_synced', 'created_at', 'updated_at'
        ]


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer model (PSE-2).
    
    Attributes:
        id (int): Customer ID.
        first_name (str): First name.
        last_name (str): Last name.
        document_number (str): Document number (CI / RUC).
        client_type (str): Client segmentation.
        email (str): Email.
        phone (str): Phone.
        address (str): Address.
        is_active (bool): Active status.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Update timestamp.
    """
    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'document_number',
            'client_type', 'email', 'phone', 'address',
            'is_active', 'created_at', 'updated_at'
        ]
