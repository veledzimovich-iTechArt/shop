from decimal import Decimal

from django.contrib.postgres.fields import CICharField
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import MinValueValidator
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import as_serializer_error

from django.db import models
from shops.models import Shop
from users.models import User
from units.utils import UnitsUtil, AMOUNT_ERROR_MESSAGE

# Create your models here.


class Unit(models.Model):
    shop = models.ForeignKey(
        Shop, related_name='units', on_delete=models.CASCADE
    )
    name = CICharField(max_length=128)
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal(1),
        validators=[MinValueValidator(Decimal())]
    )
    price = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=Decimal(1),
        validators=[MinValueValidator(Decimal())]
    )
    amount = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        ordering = ['shop__name', 'name', 'price']
        unique_together = ['name', 'weight', 'shop_id']

    def __str__(self):
        return f'{self.name} [{self.shop}]'

    @property
    def price_for_kg(self) -> 'Decimal':
        return round((Decimal(1) / self.weight) * self.price, 2)


class ReservedUnit(models.Model):
    user = models.ForeignKey(
        User, related_name='reserved_units', on_delete=models.CASCADE
    )
    unit = models.ForeignKey(
        Unit, related_name='reserved_units', on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    is_cleaned = False

    class Meta:
        ordering = ['unit__shop__name', 'unit__name', 'unit__price']
        unique_together = ['user_id', 'unit_id']

    def __str__(self):
        return f'{self.unit} ({self.user})'

    @property
    def total(self) -> 'Decimal':
        return round(self.unit.price * Decimal(self.amount), 2)

    def clean(self, is_deleted: bool = False) -> None:
        self.is_cleaned = True

        old_instance = ReservedUnit.objects.filter(id=self.id).first()

        if is_deleted:
            amount = self.unit.amount + self.amount
        else:
            amount = (
                self.unit.amount - (self.amount - old_instance.amount)
                if old_instance else self.unit.amount - self.amount
            )

        try:
            UnitsUtil().update_unit_amount(self.unit, amount)
        except ValidationError as err:
            raise DjangoValidationError(
                {'amount': f'{AMOUNT_ERROR_MESSAGE} {abs(amount)}'},
                code='limit_value'
            ) from err


@receiver(pre_save, sender=ReservedUnit)
def update_reserved_hook(
    sender: ReservedUnit, instance: ReservedUnit, using: str, **kwargs
) -> None:

    if not instance.is_cleaned:
        try:
            instance.clean()
        except DjangoValidationError as err:
            raise ValidationError(
                detail=as_serializer_error(err)
            ) from err


@receiver(post_delete, sender=ReservedUnit)
def delete_reserved_hook(
    sender: ReservedUnit, instance: ReservedUnit, using: str, **kwargs
) -> None:

    if not instance.is_cleaned:
        try:
            instance.clean(True)
        except DjangoValidationError as err:
            raise ValidationError(
                detail=as_serializer_error(err)
            ) from err
