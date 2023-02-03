from rest_framework import serializers

from units.models import ReservedUnit, Unit


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
