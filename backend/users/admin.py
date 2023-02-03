from decimal import Decimal
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import AppAccount, User
# Register your models here.


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            'Additional info', {'fields': ('phone', )},
        ),
        (
            'App account', {
                'fields': ('get_app_account', 'get_app_account_amount')
            }
        )
    )
    readonly_fields = ('get_app_account', 'get_app_account_amount')

    def get_app_account(self, value: User) -> str:
        return value.app_account
    get_app_account.short_description = 'App account'

    def get_app_account_amount(self, value: User) -> Decimal:
        return value.app_account.amount
    get_app_account_amount.short_description = 'Amount'


class AppAccountAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'amount'
    )
    fields = ('user', 'amount')
    readonly_fields = ('user',)


admin.site.register(AppAccount, AppAccountAdmin)
admin.site.register(User, CustomUserAdmin)
