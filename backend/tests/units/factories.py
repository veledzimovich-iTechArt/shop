import factory
from tests.shops.factories import ShopFactory
from units.models import ReservedUnit, Unit
from tests.users.factories import UserFactory


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
