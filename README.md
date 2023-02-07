# shop

## DjangoRest

# Content

[Django filters](#django-filters)

[Serializer read write only](#serializer-read-write-only)

[Signals](#signals)

[Atomic](#atomic)

[Allowed http methods](#allowed-http-methods)


# Django filters

```bash
pip install django-filter
```

1. api/settings.py
```python
INSTALLED_APPS = [
    #...
    'django_filters',
    #...
]
# ...
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ]
}
```
2. units/views.py
```python

class UnitView(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
# ...
    filter_backends = [
        DjangoFilterBackend, OrderingByPropertyFilter, SearchFilter
    ]
    filterset_fields = ['shop__name', 'name']
    ordering_fields = ['shop__name', 'name', 'price', 'price_for_kg']
    property_ordering_fields = ['price_for_kg']
    ordering = ['shop__name', 'name', 'price']
    search_fields = ['name', '=price']

class ReservedUnitView(viewsets.ModelViewSet):
# ...
    filterset_fields = ['unit__shop__name', 'unit__name']
    ordering_fields = [
        'unit__shop__name', 'unit__name', 'unit__price', 'unit__price_for_kg'
    ]
    property_ordering_fields = ['unit__price_for_kg']
    ordering = ['unit__shop__name', 'unit__name', 'unit__price']
    search_fields = ['unit__name', '=unit__price']
    http_method_names = ['get', 'head', 'options', 'post', 'patch', 'delete']
```
3. units/filters.py
```python
from operator import attrgetter
from typing import TYPE_CHECKING

from django.db.models import Case, When
from rest_framework.filters import OrderingFilter

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from rest_framework.request import Request

    from units.views import UnitView


class OrderingByPropertyFilter(OrderingFilter):

    def get_property_ordering_fields(self, view: 'UnitView') -> 'list':
        property_ordering = getattr(
            view, 'property_ordering_fields', []
        )
        return [
            *property_ordering,
            *[f'-{field}' for field in property_ordering]
        ]

    def get_property_order_expression(
        self, order: str, queryset: 'QuerySet'
    ) -> 'Case':
        desc = '-' in order
        order = order.replace('-', '').replace('__', '.')

        queryset_sorted = sorted(
            [(item.id, attrgetter(order)(item)) for item in queryset],
            key=lambda x: x[1],
            reverse=desc
        )
        index_list = [idx for idx, _ in queryset_sorted]

        return Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(index_list)]
        )

    def filter_queryset(
        self, request: 'Request', queryset: 'QuerySet', view: 'UnitView'
    ) -> 'QuerySet':
        ordering = self.get_ordering(request, queryset, view)
        property_ordering = self.get_property_ordering_fields(view)

        if ordering:
            final_ordering = []
            for order in ordering:
                if order in property_ordering:
                    final_ordering.append(
                        self.get_property_order_expression(order, queryset)
                    )
                else:
                    final_ordering.append(order)
            return queryset.order_by(*final_ordering)
        return queryset
```

# Serializer read write only

```python
class ReservedUnitSerializer(serializers.ModelSerializer):
    # allows to use one serializer for get/update with nested fields
    user_id = serializers.IntegerField(write_only=True)
    user = serializers.ReadOnlyField(source='user.username', read_only=True)
    unit_id = serializers.IntegerField(write_only=True)
    unit = UnitSerializer(read_only=True)

    class Meta:
        model = ReservedUnit
        fields = ('id', 'user', 'user_id', 'unit', 'unit_id', 'amount', 'total')

    def validate_unit_id(self, value: int) -> int:
        if value not in Unit.objects.values_list('id', flat=True):
            raise ValidationError('Unit does not exist')
        return value

    def validate_user_id(self, value: int) -> int:
        if value not in User.objects.values_list('id', flat=True):
            raise ValidationError('User does not exist')
        return value
```

# Signals

1. units/models.py
```python
@receiver(post_delete, sender=ReservedUnit)
def delete_reserved_hook(
    sender: ReservedUnit, instance: ReservedUnit, using: str, **kwargs
) -> None:

    if not instance.is_cleaned:
        try:
            instance.clean(True)
            instance._process_update_unit_amount()
        except ValidationError as err:
            raise RestValidationError(
                detail=as_serializer_error(err)
            ) from err
```
2. users/models.py
```python
@receiver(post_save, sender=User)
def create_account_hook(
    sender: User, instance: User, using: str, **kwargs
) -> None:
    if not hasattr(instance, 'app_account'):
        AppAccount.objects.create(user=instance)
```

# Atomic

1. api/urls.py
```python
router = routers.DefaultRouter()
router.register(r'units', UnitView, 'unit')
router.register(r'reserved-units', ReservedUnitView, 'reserved-unit')
```

2. units/views.py
```python
# ...
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
```

# Allowed http methods

1. users/views.py
```python
class AppAccountView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = AppAccount.objects.all()
    serializer_class = AppAccountSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'head', 'options', 'patch']
```

2. api/tests/users/views.py
```python
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
```
