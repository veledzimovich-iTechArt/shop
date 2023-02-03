# sourcery skip: snake-case-functions
from rest_framework import status
from tests.shops.base import BaseShopTest


class TestShopView(BaseShopTest):
    def test__get_shop_list_unauthorised__forbidden(self) -> None:
        response = self.client.get(self.shops_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test__shop_list_unsafe_methods__not_allowed(self) -> None:
        self.client.force_login(self.user)
        for method in ['post', 'put', 'patch', 'delete']:
            call_method = getattr(self.client, method.lower())
            response = call_method(self.shops_list_url)
            self.assertEqual(
                response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
            )
            response = call_method(self.shops_detail_url)
            self.assertEqual(
                response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
            )

    def test__get_shops_list_authorised__success(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(self.shops_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.shops))

    def test__get_shops_detail_authorised__success(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(self.shops_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.shops[0].id)
        self.assertEqual(response.data['name'], self.shops[0].name)
