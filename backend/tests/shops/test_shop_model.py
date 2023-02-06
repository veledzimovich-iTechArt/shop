# sourcery skip: snake-case-functions
from django.test import TestCase
from django.db.utils import IntegrityError

from tests.shops.factories import ShopFactory


class TestShopsModel(TestCase):

    def setUp(self) -> None:
        self.shop = ShopFactory()

    def test_name_case_insensitive_unique(self) -> None:
        shop = ShopFactory()
        shop.name = self.shop.name.upper()

        try:
            shop.save(update_fields=('name',))
        except IntegrityError as err:
            self.assertEqual(type(err), IntegrityError)
        else:
            self.fail('IntegrityError not raised')
