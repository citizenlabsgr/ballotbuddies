import factory

from ..models import Profile


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
