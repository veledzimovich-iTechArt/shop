# Shop
## DjangoRest

# Content

```bash
pip install django-filter
```

settings.py
```python
INSTALLED_APPS = [
    ...
    'django_filters',
    ...
]
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ]
}
```

units/views.py
```python

class UnitView(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
# ...
    ordering_fields = ['shop__name', 'name', 'price', 'price_for_kg']
    property_ordering_fields = ['price_for_kg']
# ...

class ReservedUnitView(viewsets.ModelViewSet):
# ...
ordering_fields = [
        'unit__shop__name', 'unit__name', 'unit__price', 'unit__price_for_kg'
    ]
property_ordering_fields = ['unit__price_for_kg']
# ...
```

Create own filter to order using property
units/filters.py
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
