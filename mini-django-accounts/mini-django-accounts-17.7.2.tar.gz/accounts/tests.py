from django.contrib.auth import get_user_model
from django.test import TestCase


class TestUserModel(TestCase):
    def test_create_user_method1(self):
        # Arrange, Act, Assert
        User = get_user_model()

        user = User(
            email="chaosengine256@gmail.com",
            name="Chaos Engine"
        )

        user.save()

        find_user = User.objects.get(email="chaosengine256@gmail.com")
        self.assertEqual(user.pk, find_user.pk)

    def test_create_user_method2(self):
        # Arrange, Act, Assert
        User = get_user_model()

        user = User.objects.create_user(email="chaosengine256@gmail.com", name="Chaos Engine")

        find_user = User.objects.get(email="chaosengine256@gmail.com")
        self.assertEqual(user.pk, find_user.pk)

    def test_create_superuser(self):
        # Arrange, Act, Assert
        User = get_user_model()

        user = User.objects.create_superuser(email="chaosengine256@gmail.com", name="Chaos Engine", password="hello")

        find_user = User.objects.get(email="chaosengine256@gmail.com")
        self.assertEqual(user.pk, find_user.pk)

    def test_user_name(self):
        # Arrange, Act, Assert
        User = get_user_model()

        user = User.objects.create_user(email="chaosengine256@gmail.com", name="Chaos Engine", password="hello")

        self.assertEqual(user.get_full_name(), "Chaos Engine")
        self.assertEqual(user.get_short_name(), "Chaos Engine")
