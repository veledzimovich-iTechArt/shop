from django.contrib.postgres.fields import CICharField
from django.db import models

# Create your models here.


class Shop(models.Model):
    name = CICharField(max_length=128)

    def __str__(self) -> str:
        return self.name
