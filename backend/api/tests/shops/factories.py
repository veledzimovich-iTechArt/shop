import factory
from shops.models import Shop


class ShopFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shop

    name = factory.Faker('company')
