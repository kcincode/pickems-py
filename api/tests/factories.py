import factory
from api.models import *


class PickemsUserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('company_email')

    class Meta:
        model = PickemsUser
