from decimal import Decimal
from typing import TYPE_CHECKING

from django.contrib import admin

from units.models import ReservedUnit, Unit

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from rest_framework.request import Request

# Register your models here.


class UnitAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'shop', 'name', 'weight', 'price', 'price_for_kg', 'amount'
    )
    fields = ('shop', 'name', 'weight', 'price', 'amount')

    def get_queryset(self, request: 'Request') -> 'QuerySet':
        return super().get_queryset(request).select_related('shop')


class ReservedUnitAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'get_shop',
        'get_unit',
        'get_weight',
        'get_price',
        'get_price_for_kg',
        'amount',
        'total'
    )
    fields = ('user', 'unit', 'amount')

    def get_queryset(self, request: 'Request') -> 'QuerySet':
        return (
            super().get_queryset(request)
            .select_related(
                'user', 'unit__shop'
            )
        )

    def get_shop(self, value: 'ReservedUnit') -> 'Decimal':
        return value.unit.shop.name
    get_shop.short_description = 'Shop'

    def get_unit(self, value: 'ReservedUnit') -> 'Decimal':
        return value.unit.name
    get_unit.short_description = 'Name'

    def get_weight(self, value: 'ReservedUnit') -> 'Decimal':
        return value.unit.weight
    get_weight.short_description = 'Weight'

    def get_price(self, value: 'ReservedUnit') -> 'Decimal':
        return value.unit.price
    get_price.short_description = 'Price'

    def get_price_for_kg(self, value: 'ReservedUnit') -> 'Decimal':
        return value.unit.price_for_kg
    get_price_for_kg.short_description = 'Price for kg'


admin.site.register(ReservedUnit, ReservedUnitAdmin)
admin.site.register(Unit, UnitAdmin)
