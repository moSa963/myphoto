from django.contrib.auth import get_user_model


def create_user(**args):
    return get_user_model().objects.create_user(**args)