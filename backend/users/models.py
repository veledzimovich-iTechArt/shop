from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save

# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=32, verbose_name='Phone', null=True, blank=True
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return self.username

    # @property
    # def app_account(self) -> 'AppAccount':
    #     return AppAccount.objects.get_or_create(user=self)[0]


@receiver(post_save, sender=User)
def create_account_hook(
    sender: User, instance: User, using: str, **kwargs
) -> None:
    if not hasattr(instance, 'app_account'):
        AppAccount.objects.create(user=instance)


class AppAccount(models.Model):
    user = models.OneToOneField(
        User, related_name='app_account', unique=True, on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal(),
        validators=[MinValueValidator(Decimal())]
    )

    def __str__(self) -> str:
        return f'{self.id}'
