from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from units.models import ReservedUnit, Unit
from users.models import User


class UnitSerializer(serializers.ModelSerializer):
    shop = serializers.ReadOnlyField(source='shop.name')

    class Meta:
        model = Unit
        fields = (
            'id', 'shop', 'name', 'weight', 'price', 'amount', 'price_for_kg'
        )


class ReservedUnitSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    user = serializers.ReadOnlyField(source='user.username', read_only=True)
    unit_id = serializers.IntegerField(write_only=True)
    unit = UnitSerializer(read_only=True)

    class Meta:
        model = ReservedUnit
        fields = ('id', 'user', 'user_id', 'unit', 'unit_id', 'amount', 'total')

    def validate_unit_id(self, value: int) -> int:
        if value not in Unit.objects.values_list('id', flat=True):
            raise ValidationError('Unit does not exist')
        return value

    def validate_user_id(self, value: int) -> int:
        if value not in User.objects.values_list('id', flat=True):
            raise ValidationError('User does not exist')
        return value
