# sourcery skip: snake-case-functions
from decimal import Decimal
from rest_framework import status

from tests.units.base import BaseUnitsTest, BaseReservedUnitsTest
from units.models import ReservedUnit
from units.utils import AMOUNT_ERROR_MESSAGE


class TestUnitsView(BaseUnitsTest):
    def test__get_unit_list_unauthorised__forbidden(self) -> None:
        response = self.client.get(self.units_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test__unit_list_unsafe_methods__not_allowed(self) -> None:
        self.client.force_login(self.user)
        for method in ['post',]:
            call_method = getattr(self.client, method.lower())
            response = call_method(self.units_list_url)
            self.assertEqual(
                response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
            )

    def test__unit_detail_unsafe_methods__not_allowed(self) -> None:
        self.client.force_login(self.user)
        for method in ['put', 'patch', 'delete']:
            call_method = getattr(self.client, method.lower())
            response = call_method(self.units_detail_url)
            self.assertEqual(
                response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
            )

    def test__get_search_by_same_name_units_list__success(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(
            f'{self.units_list_url}?search={self.units[0].name}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test__get_search_by_name_units_list__success(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(
            f'{self.units_list_url}?search={self.units[1].name}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test__get_filtered_by_shop_units_list__success(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(
            f'{self.units_list_url}?shop__name={self.units[0].shop.name}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test__get_filtered_by_name_units_list__success(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(
            f'{self.units_list_url}?name={self.units[0].name}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test__get_filtered_by_shop_and_unit_units_list__success(self) -> None:
        self.client.force_login(self.user)
        filters = f'shop__name={self.units[0].shop.name}&name={self.units[0].name}'
        response = self.client.get(
            f'{self.units_list_url}?{filters}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test__get_units_list__success(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(self.units_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.units))
        # check default ordering
        srt = [
            i['id'] for i in sorted(
                response.data,
                key=lambda x: (
                    x['shop'],
                    x['name'],
                    x['price']
                )
            )
        ]

        self.assertEqual(srt, [i['id'] for i in response.data])

    def test__get_units_list_ordering_by_price_for_kg_reversed___success(
        self
    ) -> None:
        self.client.force_login(self.user)
        ordering = '-price_for_kg'
        response = self.client.get(
            f'{self.units_list_url}?ordering={ordering}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.units))

        srt = [
            i['id'] for i in sorted(
                response.data,
                key=lambda x: (
                    x['price_for_kg']
                ),
                reverse=True
            )]
        self.assertEqual(srt, [i['id'] for i in response.data])

    def test__get_units_detail__success(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(self.units_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.units[0].id)
        self.assertEqual(response.data['name'], self.units[0].name)
        self.assertEqual(
            Decimal(response.data['weight']), self.units[0].weight)
        self.assertEqual(response.data['amount'], self.units[0].amount)
        self.assertEqual(
            Decimal(response.data['price']), self.units[0].price
        )
        self.assertEqual(
            response.data['price_for_kg'],
            round((Decimal(1) / self.units[0].weight) * self.units[0].price, 2)
        )


class TestReservedUnitsView(BaseReservedUnitsTest):

    def test__get_reserved_units_list_unauthorised__forbidden(self) -> None:
        response = self.client.get(self.reserved_units_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test__reserved_units_list_put__not_allowed(self) -> None:
        self.client.force_login(self.user)

        response = self.client.put(
            self.reserved_units_detail_url,
            data={
                'user_id': self.user.id,
                'unit_id': self.reserved_units[0].id
            },
            format='json'
        )
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test__get_search_by_same_name_reserved_units_list__success(
        self
    ) -> None:
        self.client.force_login(self.user)
        response = self.client.get(
            f'{self.reserved_units_list_url}?search={self.reserved_units[0].unit.name}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test__get_search_by_name_reserved_units_list__success(
        self
    ) -> None:
        self.client.force_login(self.user)
        response = self.client.get(
            f'{self.reserved_units_list_url}?search={self.reserved_units[1].unit.name}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test__get_filtered_by_shop_reserved_units_list__success(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(
            f'{self.reserved_units_list_url}?unit__shop__name={self.reserved_units[0].unit.shop.name}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test__get_filtered_by_unit_name_reserved_units_list__success(
        self
    ) -> None:
        self.client.force_login(self.user)
        filters = f'unit__name={self.reserved_units[0].unit.name}'
        response = self.client.get(
            f'{self.reserved_units_list_url}?{filters}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test__get_filtered_by_shop_and_unit_name_reserved_units_list__success(
        self
    ) -> None:
        self.client.force_login(self.user)
        filters = f'unit__shop__name={self.reserved_units[0].unit.shop.name}&unit__name={self.reserved_units[0].unit.name}'
        response = self.client.get(
            f'{self.reserved_units_list_url}?{filters}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test__get_reserved_units_list__success(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(self.reserved_units_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.reserved_units))
        # check default ordering
        srt = [
            i['id'] for i in sorted(
                response.data,
                key=lambda x: (
                    x['unit']['shop'],
                    x['unit']['name'],
                    x['unit']['price']
                )
            )
        ]

        self.assertEqual(srt, [i['id'] for i in response.data])

    def test__get_reserved_units_list_ordered_by_price_for_kg_reversed__success(
        self
    ) -> None:
        self.client.force_login(self.user)
        ordering = '-unit__price_for_kg'
        response = self.client.get(
            f'{self.reserved_units_list_url}?ordering={ordering}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.reserved_units))

        srt = [
            i['id'] for i in sorted(
                response.data,
                key=lambda x: (
                    x['unit']['price_for_kg']
                ),
                reverse=True
            )
        ]

        self.assertEqual(srt, [i['id'] for i in response.data])

    def test__get_reserved_units_list_ordered_by_shop_unit_price_for_kg__success(
        self
    ) -> None:
        self.client.force_login(self.user)
        ordering = 'unit__shop__name,unit__name,unit__price_for_kg'
        response = self.client.get(
            f'{self.reserved_units_list_url}?ordering={ordering}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.reserved_units))
        srt = [
            i['id'] for i in sorted(
                response.data,
                key=lambda x: (
                    x['unit']['shop'],
                    x['unit']['name'],
                    x['unit']['price_for_kg']
                )
            )
        ]

        self.assertEqual(srt, [i['id'] for i in response.data])

    def test__get_reserved_units_list_ordered_by_shop_price_for_kg_reversed_success(
        self
    ) -> None:
        self.client.force_login(self.user)
        ordering = 'unit__shop__name,-unit__price_for_kg'
        response = self.client.get(
            f'{self.reserved_units_list_url}?ordering={ordering}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.reserved_units))

        reserved_ids = [i['id'] for i in response.data]
        if (
            self.reserved_units[0].unit.price_for_kg
            > self.reserved_units[1].unit.price_for_kg
        ):
            self.assertTrue(
                reserved_ids.index(self.reserved_units[0].id)
                < reserved_ids.index(self.reserved_units[1].id)
            )
        else:
            self.assertTrue(
                reserved_ids.index(self.reserved_units[0].id)
                > reserved_ids.index(self.reserved_units[1].id)
            )

    def test__get_reserved_units_list_ordered_by_unit_price_for_kg_success(
        self
    ) -> None:
        self.client.force_login(self.user)
        ordering = '-unit__name,unit__price_for_kg'
        response = self.client.get(
            f'{self.reserved_units_list_url}?ordering={ordering}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.reserved_units))

        reserved_ids = [i['id'] for i in response.data]
        if (
            self.reserved_units[0].unit.price_for_kg
            > self.reserved_units[2].unit.price_for_kg
        ):
            self.assertTrue(
                reserved_ids.index(self.reserved_units[0].id)
                > reserved_ids.index(self.reserved_units[2].id)
            )
        else:
            self.assertTrue(
                reserved_ids.index(self.reserved_units[0].id)
                < reserved_ids.index(self.reserved_units[2].id)
            )

    def test__get_other_reserved_units_list__success(self) -> None:
        self.client.force_login(self.other_reserved_unit.user)
        response = self.client.get(self.reserved_units_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test__get_reserved_units_detail__success(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(self.reserved_units_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.reserved_units[0].id)
        self.assertEqual(
            response.data['user'], self.reserved_units[0].user.username
        )
        self.assertEqual(
            response.data['unit']['id'], self.reserved_units[0].unit_id
        )
        self.assertEqual(
            response.data['amount'], self.reserved_units[0].amount
        )
        self.assertEqual(
            response.data['total'],
            round(
                self.reserved_units[0].unit.price
                * Decimal(self.reserved_units[0].amount), 2
            )
        )

    def test__post_reserved_units_list__created(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            self.reserved_units_list_url,
            data={
                'user_id': self.user.id,
                'unit_id': self.other_unit.id
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            response.data['user'], self.reserved_units[0].user.username
        )
        self.assertEqual(
            response.data['unit']['id'], self.other_unit.id
        )
        self.assertEqual(
            response.data['amount'], 1
        )

    def test__post_same_reserved_units_list__success(self) -> None:
        self.client.force_login(self.other_reserved_unit.user)
        initial_amount = self.other_reserved_unit.amount
        response = self.client.post(
            self.reserved_units_list_url,
            data={
                'user_id': self.other_reserved_unit.user.id,
                'unit_id': self.other_reserved_unit.unit.id,
                'amount': initial_amount
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], initial_amount)
        self.assertEqual(self.other_reserved_unit.amount, initial_amount)

    def test__post_exceed_reserved_units_list__created(self) -> None:
        self.client.force_login(self.user)
        exceed = 1
        response = self.client.post(
            self.reserved_units_list_url,
            data={
                'user_id': self.user.id,
                'unit_id': self.other_unit.id,
                'amount': self.other_unit.amount + exceed
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['amount'][0], f'{AMOUNT_ERROR_MESSAGE} {exceed}'
        )

    def test__patch_reserved_units_detail__success(self) -> None:
        self.client.force_login(self.user)
        response = self.client.patch(
            self.reserved_units_detail_url,
            data={
                'amount': self.reserved_units[0].unit.amount
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reserved_units[0].refresh_from_db()
        self.assertEqual(response.data['id'], self.reserved_units[0].id)
        self.assertEqual(
            response.data['user'], self.reserved_units[0].user.username
        )
        self.assertEqual(
            response.data['unit']['id'], self.reserved_units[0].unit_id
        )
        self.assertEqual(
            response.data['amount'], self.reserved_units[0].amount
        )

    def test__patch_exceed_reserved_units_detail__bad_request(self) -> None:
        self.client.force_login(self.user)
        exceed = 2
        response = self.client.patch(
            self.reserved_units_detail_url,
            data={
                'amount': (
                    self.reserved_units[0].amount
                    + self.reserved_units[0].unit.amount
                    + exceed
                )
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['amount'][0], f'{AMOUNT_ERROR_MESSAGE} {exceed}'
        )

    def test__patch_reserved_unit_detail_not_owner__not_found(self) -> None:
        self.client.force_login(self.user)
        response = self.client.patch(
            self.other_reserved_unit_detail_url,
            data={
                'amount': self.other_reserved_unit.unit.amount
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test__delete_reserved_units_detail__no_content(self) -> None:
        self.client.force_login(self.user)
        response = self.client.delete(self.reserved_units_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test__delete_reserved_units_detail_not_owner__not_found(
        self
    ) -> None:
        self.client.force_login(self.user)
        response = self.client.delete(self.other_reserved_unit_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test__bye_reserved_units__success(self) -> None:
        self.client.force_login(self.user)
        initial_app_account_amount = self.user.app_account.amount
        response = self.client.post(self.reserved_units_bye_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ReservedUnit.objects.filter(user_id=self.user.id).count(), 0
        )

        self.user.app_account.refresh_from_db()
        self.assertEqual(
            response.data['total'], initial_app_account_amount
        )
        self.assertEqual(
            self.user.app_account.amount, Decimal()
        )

    def test__bye_other_reserved_unit_with_zero_app_account__bad_request(
        self
    ) -> None:
        user = self.other_reserved_unit.user
        self.client.force_login(user)
        initial_app_account_amount = user.app_account.amount
        response = self.client.post(self.reserved_units_bye_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            ReservedUnit.objects.filter(user_id=user.id).count(), 1
        )
        user.app_account.refresh_from_db()
        self.assertEqual(
            user.app_account.amount, initial_app_account_amount
        )
        self.assertEqual(
            response.data['amount'][0],
            f'{AMOUNT_ERROR_MESSAGE} {self.other_reserved_unit.total}'
        )

    def test__clear_reserved_units__no_content(self) -> None:
        self.client.force_login(self.user)
        initial_app_account_amount = self.user.app_account.amount
        initial_amounts = {
            ru.id: (ru.unit.amount, ru.amount) for ru in self.reserved_units
        }

        response = self.client.delete(self.reserved_units_clear_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            ReservedUnit.objects.filter(user_id=self.user.id).count(), 0
        )

        self.user.app_account.refresh_from_db()
        self.assertEqual(
            self.user.app_account.amount, initial_app_account_amount
        )
        for reserved_unit in self.reserved_units:
            reserved_unit.unit.refresh_from_db(fields=('amount',))
            self.assertEqual(
                reserved_unit.unit.amount,
                sum(initial_amounts[reserved_unit.id])
            )

    def test__get_search_by_not_admin_user_reserved_units_list__forbidden(
        self
    ) -> None:
        self.client.force_login(self.user)
        response = self.client.get(self.reserved_units_search_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test__get_search_by_admin_user_reserved_units_list__success(
        self
    ) -> None:
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save(update_fields=('is_staff', 'is_superuser'))
        self.client.force_login(self.user)
        response = self.client.get(self.reserved_units_search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
