from decimal import Decimal
from typing import TYPE_CHECKING

from django.db.transaction import atomic
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error

from units.filters import OrderingByPropertyFilter
from units.permissions import IsOwnerOrReadOnly
from units.serializers import ReservedUnitSerializer, UnitSerializer
from units.models import ReservedUnit, Unit
from units.utils import AMOUNT_ERROR_MESSAGE
from users.serializers import AppAccountSerializer


if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from rest_framework.request import Request

# Create your views here.


class UnitView(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = UnitSerializer
    queryset = (
        Unit.objects.select_related('shop')
    )
    filter_backends = [
        DjangoFilterBackend, OrderingByPropertyFilter, SearchFilter
    ]
    filterset_fields = ['shop__name', 'name']
    ordering_fields = ['shop__name', 'name', 'price', 'price_for_kg']
    property_ordering_fields = ['price_for_kg']
    ordering = ['shop__name', 'name', 'price']
    search_fields = ['name', '=price']


class ReservedUnitView(viewsets.ModelViewSet):
    serializer_class = ReservedUnitSerializer

    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [
        DjangoFilterBackend, OrderingByPropertyFilter, SearchFilter
    ]
    filterset_fields = ['unit__shop__name', 'unit__name']
    ordering_fields = [
        'unit__shop__name', 'unit__name', 'unit__price', 'unit__price_for_kg'
    ]
    property_ordering_fields = ['unit__price_for_kg']
    ordering = ['unit__shop__name', 'unit__name', 'unit__price']
    search_fields = ['unit__name', '=unit__price']
    http_method_names = ['get', 'head', 'options', 'post', 'patch', 'delete']

    def get_queryset(self) -> 'QuerySet':
        return (
            ReservedUnit.objects
            .filter(user_id=self.request.user.id)
            .select_related('user', 'unit__shop')
        )

    @atomic
    def __process_buying(
        self, request: 'Request', queryset: 'QuerySet', total: Decimal
    ) -> None:
        amount = request.user.app_account.amount - total
        app_acount_serializer = AppAccountSerializer(
            request.user.app_account,
            data={'amount': amount}
        )
        try:
            app_acount_serializer.is_valid(raise_exception=True)
        except ValidationError as err:
            err.detail = {'amount': f'{AMOUNT_ERROR_MESSAGE} {abs(amount)}'}
            raise ValidationError(
                detail=as_serializer_error(err)
            ) from err

        app_acount_serializer.save()

        queryset._raw_delete(queryset.db)

    @action(detail=False, methods=['post'])
    def buy(self, request: 'Request') -> Response:
        queryset = self.get_queryset()
        total = Decimal(sum(reserved_unit.total for reserved_unit in queryset))

        self.__process_buying(request, queryset, total)
        return Response(
            data={'total': total}, status=status.HTTP_200_OK
        )

    @atomic
    def __process_clear(self) -> None:
        queryset = self.get_queryset()
        to_update_units = []
        for reserved_unit in queryset:
            to_update_units.append(reserved_unit.unit)
            reserved_unit.unit.amount += reserved_unit.amount

        Unit.objects.bulk_update(to_update_units, fields=('amount',))

        queryset._raw_delete(queryset.db)

    @ action(detail=False, methods=['delete'])
    def clear(self, request: 'Request') -> Response:
        self.__process_clear()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ReservedUnitsSearchView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ReservedUnitSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self) -> 'QuerySet':
        username = self.kwargs.get('username')
        return ReservedUnit.objects.filter(user__username=username)
