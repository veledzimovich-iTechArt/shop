# sourcery skip: snake-case-functions
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from tests.users.factories import UserFactory


class BaseUsersTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.admin = UserFactory(is_staff=True, is_superuser=True)

        cls.user_list_url = reverse_lazy('user-list')
        cls.user_detail_url = reverse_lazy(
            'user-detail', args=(cls.user.id,)
        )

        cls.app_account_list_url = reverse_lazy('app_account-list')
        cls.app_account_detail_url = reverse_lazy(
            'app_account-detail', args=(cls.user.app_account.id,)
        )
