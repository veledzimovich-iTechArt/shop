from rest_framework import serializers

from users.models import AppAccount, User


class AppAccountSerializer(serializers.ModelSerializer):
    # amount = serializers.DecimalField(
    #     max_digits=12, decimal_places=2, min_value=0,
    #     error_messages={
    #         **serializers.DecimalField.default_error_messages,
    #         'min_value': 'The limit have been exceeded by {min_value}.'
    #     }
    # )

    class Meta:
        model = AppAccount
        fields = ['id', 'amount']


class UserSerializer(serializers.ModelSerializer):
    app_account = AppAccountSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'app_account']
