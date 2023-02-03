from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from units.models import Unit


AMOUNT_ERROR_MESSAGE = 'The limit have been exceeded by'


class UnitsUtil:

    def update_unit_amount(self, instance: 'Unit', amount: int) -> None:
        from units.serializers import UnitSerializer
        data = UnitSerializer(instance).data
        data.pop('id')
        data['amount'] = amount
        unit_serializer = UnitSerializer(
            instance,
            data=data
        )
        unit_serializer.is_valid(raise_exception=True)
        unit_serializer.save()
