# sourcery skip: snake-case-functions
from django.test import TestCase
from django.db.utils import IntegrityError

from tests.units.factories import ReservedUnitFactory, UnitFactory


class TestUnitsModel(TestCase):

    def setUp(self) -> None:
        self.unit = UnitFactory()

    def test_name_weight_shop_id_unique_together(self) -> None:
        unit = UnitFactory()
        unit.name = self.unit.name.upper()
        unit.weight = self.unit.weight
        unit.shop_id = self.unit.shop_id

        try:
            unit.save(update_fields=('name', 'weight', 'shop_id'))
        except IntegrityError as err:
            self.assertEqual(type(err), IntegrityError)
        else:
            self.fail('IntegrityError not raised')


class TestReservedUnitsModel(TestCase):

    def setUp(self) -> None:
        self.reserved_unit = ReservedUnitFactory()

    def test_name_weight_shop_id_unique_together(self) -> None:
        reserved_unit = ReservedUnitFactory()
        reserved_unit.user_id = self.reserved_unit.user_id
        reserved_unit.unit_id = self.reserved_unit.unit_id

        try:
            reserved_unit.save(update_fields=('user_id', 'unit_id'))
        except IntegrityError as err:
            self.assertEqual(type(err), IntegrityError)
        else:
            self.fail('IntegrityError not raised')
