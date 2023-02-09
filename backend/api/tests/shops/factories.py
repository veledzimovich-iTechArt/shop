import factory
from shops.models import Shop


class ShopFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shop

    name = factory.Sequence(lambda n: f'Company {n}')
