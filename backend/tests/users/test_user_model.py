# sourcery skip: snake-case-functions
from django.test import TestCase
from django.db.utils import IntegrityError

from tests.users.factories import UserFactory


class TestUnitsModel(TestCase):

    def setUp(self) -> None:
        self.user = UserFactory()

    def test_email_unique(self) -> None:
        user = UserFactory()
        user.email = self.user.email

        try:
            user.save(update_fields=('email',))
        except IntegrityError as err:
            self.assertEqual(type(err), IntegrityError)
        else:
            self.fail('IntegrityError not raised')

    def test_username_unique(self) -> None:
        user = UserFactory()
        user.username = self.user.username

        try:
            user.save(update_fields=('username',))
        except IntegrityError as err:
            self.assertEqual(type(err), IntegrityError)
        else:
            self.fail('IntegrityError not raised')

    def test_phone_is_none(self) -> None:
        user = UserFactory(phone=None)
        self.assertIsNone(user.phone)
