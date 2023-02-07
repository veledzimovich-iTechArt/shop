# sourcery skip: snake-case-functions
from decimal import Decimal
from rest_framework import status

from api.tests.users.base import BaseUsersTest
from users.models import User


class TestUsersView(BaseUsersTest):
    def test__not_admin_user_users__forbidden(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test__users_list_put__not_allowed(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.put(self.user_detail_url)
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test__get_users_list__success(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test__get_user_detail__success(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['phone'], self.user.phone)

    def test__post_users_list_created(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.post(
            self.users_list_url,
            data={
                "username": "test",
                "first_name": "A",
                "last_name": "V",
                "email": "test@email.com",
                "phone": "123456789"
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'test')
        self.assertEqual(response.data['first_name'], 'A')
        self.assertEqual(response.data['last_name'], 'V')
        self.assertEqual(response.data['email'], 'test@email.com')
        self.assertEqual(response.data['phone'], '123456789')
        self.assertIsNotNone(response.data['app_account']['id'])

    def test__patch_user_detail_success(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.patch(
            self.user_detail_url,
            data={
                "first_name": "",
                "last_name": "",
                "email": "patch_test@email.com",
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['first_name'], '')
        self.assertEqual(response.data['last_name'], '')
        self.assertEqual(response.data['email'], 'patch_test@email.com')
        self.assertEqual(response.data['phone'], self.user.phone)

    def test__patch_account_read_only_user_detail_success(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.patch(
            self.user_detail_url,
            data={
                "app_account": {
                    "id": self.admin.app_account.id,
                    "amount": 100
                }
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data['app_account']['id'], self.user.app_account.id
        )

    def test__delete_user_detail_success(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.delete(self.user_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)


class TestAccountView(BaseUsersTest):

    def test__not_admin_user_accounts__forbidden(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(self.app_accounts_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.app_account_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test__accounts_list_unsafe_methods__not_allowed(self) -> None:
        self.client.force_login(self.admin)
        for method in ['post',]:
            call_method = getattr(self.client, method.lower())
            response = call_method(self.app_accounts_list_url)
            self.assertEqual(
                response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
            )

    def test__account_detail_unsafe_methods__not_allowed(self) -> None:
        self.client.force_login(self.admin)
        for method in ['put', 'delete']:
            call_method = getattr(self.client, method.lower())
            response = call_method(self.app_account_detail_url)
            self.assertEqual(
                response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
            )

    def test__get_accounts_list__success(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.get(self.app_accounts_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test__get_account_detail__success(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.get(self.app_account_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            Decimal(response.data['amount']), self.user.app_account.amount
        )

    def test__patch_account_detail__success(self) -> None:
        self.client.force_login(self.admin)

        initial_amount = self.user.app_account.amount
        response = self.client.patch(
            self.app_account_detail_url,
            data={
                "amount": initial_amount + Decimal('10')
            },
            format='json'
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            Decimal(response.data['amount']), initial_amount + Decimal('10.00')
        )
