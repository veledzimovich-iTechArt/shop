import factory

from api.tests.shops.factories import ShopFactory
from api.tests.users.factories import UserFactory

from units.models import ReservedUnit, Unit


class UnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Unit

    shop = factory.SubFactory(ShopFactory)
    name = factory.Faker('sentence', nb_words=2)
    weight = factory.Faker(
        'pydecimal', min_value=1, max_value=50, right_digits=2
    )
    price = factory.Faker(
        'pydecimal', min_value=1, max_value=1000, right_digits=2
    )
    amount = factory.Faker('pyint', min_value=10, max_value=100)


class ReservedUnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReservedUnit

    user = factory.SubFactory(UserFactory)
    unit = factory.SubFactory(UnitFactory)
    amount = factory.Faker('pyint', min_value=1, max_value=10)
