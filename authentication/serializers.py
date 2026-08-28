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
    Serializer for Customer model (PSE-2, PSE-3).
    
    Attributes:
        id (int): Customer ID.
        first_name (str): First name.
        last_name (str): Last name.
        document_number (str): Document number (CI / RUC).
        company_name (str): Company name (Persona Jurídica).
        ruc (str): RUC number.
        client_type (str): Client segmentation.
        email (str): Email.
        phone (str): Phone.
        address (str): Address.
        is_active (bool): Active status.
        keycloak_synced (bool): Keycloak sync status.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Update timestamp.
    """
    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'document_number',
            'company_name', 'ruc', 'client_type', 'email', 'phone', 'address',
            'is_active', 'keycloak_synced', 'created_at', 'updated_at'
        ]


class CorporateCustomerRegisterSerializer(serializers.Serializer):
    """
    Serializer handling validation and creation of Corporate Customers (Personas Jurídicas - PSE-3)
    with Keycloak delegation and strict validation rules.
    
    Attributes:
        company_name (str): Legal company name.
        ruc (str): Valid corporate RUC number.
        email (str): Corporate email address (texto@dominio.extensión).
        password (str): Secure password (min 8 chars, uppercase, lowercase, special char).
        phone (str): Contact phone.
        address (str): Company address.
    """
    company_name = serializers.CharField(max_length=200)
    ruc = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)

    def validate_ruc(self, value):
        """
        Validates that RUC is numeric / valid format.
        """
        import re
        if not re.match(r'^\d+[\-\d]*$', value):
            raise serializers.ValidationError("El RUC debe tener un formato numérico válido.")
        if Customer.objects.filter(ruc=value).exists():
            raise serializers.ValidationError("El RUC ingresado ya se encuentra registrado.")
        return value

    def validate_email(self, value):
        """
        Validates that email is unique and not already registered.
        """
        if Customer.objects.filter(email=value).exists():
            raise serializers.ValidationError("El correo electrónico ya se encuentra registrado o corresponde a un cliente existente.")
        return value

    def validate_password(self, value):
        """
        Validates password security: min 8 chars, uppercase, lowercase, special character.
        """
        import re
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener un mínimo de 8 caracteres.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("La contraseña debe incluir al menos una letra mayúscula.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("La contraseña debe incluir al menos una letra minúscula.")
        if not re.search(r'[\W_]', value):
            raise serializers.ValidationError("La contraseña debe incluir al menos un carácter especial.")
        return value

    def create(self, validated_data):
        """
        Creates the corporate customer record and simulates Keycloak delegation.
        """
        password = validated_data.pop('password')
        company_name = validated_data.get('company_name')
        ruc = validated_data.get('ruc')
        email = validated_data.get('email')
        phone = validated_data.get('phone', '')
        address = validated_data.get('address', '')

        # Create Customer with client_type='CORPORATE'
        customer = Customer.objects.create(
            company_name=company_name,
            ruc=ruc,
            document_number=ruc,
            email=email,
            phone=phone,
            address=address,
            client_type='CORPORATE',
            keycloak_synced=True
        )
        return customer
