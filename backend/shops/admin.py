from django.contrib import admin
from shops.models import Shop

# Register your models here.


class ShopAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name',
    )
    fields = ('name',)


admin.site.register(Shop, ShopAdmin)
