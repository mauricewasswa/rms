from rest_framework import serializers
from .models import RentalSite, RentalUnit, Payment
from users.models import User

class RentalSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalSite
        fields = ['id', 'name', 'address', 'admin']
        extra_kwargs = {
            'admin': {
                'required': False,
                'allow_null': True
            }
        }

    def create(self, validated_data):
        # Auto-assign admin if not provided
        if 'admin' not in validated_data:
            validated_data['admin'] = self.context['request'].user
        return super().create(validated_data)

class RentalUnitSerializer(serializers.ModelSerializer):
    current_tenant = serializers.SerializerMethodField()
    
    class Meta:
        model = RentalUnit
        fields = ['id', 'site', 'unit_number', 'description', 'rent_amount', 'status', 
                 'features', 'current_tenant', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'current_tenant']
    
    def get_current_tenant(self, obj):
        if hasattr(obj, 'tenant'):
            from users.serializers import UserSerializer
            return UserSerializer(obj.tenant).data
        return None

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'tenant', 'unit', 'amount', 'payment_method', 'status', 
                 'reference', 'payment_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'tenant', 'created_at', 'updated_at']

class CreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['unit', 'amount', 'payment_method', 'reference', 'payment_date']
    
    def validate(self, data):
        user = self.context['request'].user
        if user.role != 'TENANT':
            raise serializers.ValidationError("Only tenants can make payments.")
        
        if not hasattr(user, 'rented_unit') or user.rented_unit != data['unit']:
            raise serializers.ValidationError("You can only pay for your rented unit.")
        
        return data