# sourcery skip: snake-case-functions
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from api.tests.shops.factories import ShopFactory
from api.tests.users.factories import UserFactory


class BaseShopTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.shops = [
            ShopFactory() for _ in range(4)
        ]
        cls.shops_list_url = reverse_lazy('shop-list')
        cls.shops_detail_url = reverse_lazy(
            'shop-detail', args=(cls.shops[0].id,)
        )
