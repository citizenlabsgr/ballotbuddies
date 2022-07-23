import factory

from ..models import Voter


class VoterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Voter
