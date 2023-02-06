# sourcery skip: snake-case-functions
from decimal import Decimal
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from tests.units.factories import ReservedUnitFactory, UnitFactory
from tests.users.factories import UserFactory


class BaseUnitsTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.units = [
            UnitFactory() for _ in range(4)
        ]
        unit = cls.units[1]
        unit.shop_id = cls.units[0].shop_id
        unit.save(update_fields=('shop_id',))
        unit = cls.units[2]
        unit.name = cls.units[0].name
        unit.save(update_fields=('name',))

        cls.units_list_url = reverse_lazy('unit-list')
        cls.units_detail_url = reverse_lazy(
            'unit-detail', args=(cls.units[0].id,)
        )


class BaseReservedUnitsTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()

        cls.reserved_units = [
            ReservedUnitFactory(user=cls.user) for _ in range(10)
        ]
        reserved_unit = cls.reserved_units[1]
        reserved_unit.unit.shop_id = cls.reserved_units[0].unit.shop_id
        reserved_unit.unit.save(update_fields=('shop_id',))

        reserved_unit = cls.reserved_units[2]
        reserved_unit.unit.name = cls.reserved_units[0].unit.name
        reserved_unit.unit.save(update_fields=('name',))

        total = Decimal(
            sum(reserved_unit.total for reserved_unit in cls.reserved_units)
        )

        account = cls.user.app_account
        account.amount += total
        account.save(update_fields=('amount',))

        cls.other_unit = UnitFactory()
        cls.other_reserved_unit = ReservedUnitFactory()

        cls.reserved_units_list_url = reverse_lazy('reserved-unit-list')
        cls.reserved_units_detail_url = reverse_lazy(
            'reserved-unit-detail', args=(cls.reserved_units[0].id,)
        )
        cls.other_reserved_unit_detail_url = reverse_lazy(
            'reserved-unit-detail', args=(cls.other_reserved_unit.id,)
        )

        cls.reserved_units_bye_url = reverse_lazy(
            'reserved-unit-buy'
        )

        cls.reserved_units_clear_url = reverse_lazy(
            'reserved-unit-clear'
        )

        cls.reserved_units_search_url = reverse_lazy(
            'reserved-search-list', args=(cls.user.username,)
        )
