from django.contrib.auth import get_user_model
from django.db import IntegrityError


def create_user():
    try:
        user, created = get_user_model().objects.get_or_create(
            email="test@test.com",
            first_name="test",
            last_name="test",
        )
        if created:
            user.set_password("33992433nkl")
            user.save()
        return user
    except IntegrityError:
        pass
