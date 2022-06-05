import os
import binascii
import random
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

mobile_num_regex_validator = RegexValidator(regex="^[0-9]{9,15}$", message="Entered mobile number isn't in a right format!")

class BaseTokenGenerator:
    """
    Base Class for the Token Generators
    - Can take arbitrary args/kwargs and work with those
    - Needs to implement the "generate_token" Method
    """
    def __init__(self, *args, **kwargs):
        pass

    def generate_token(self, *args, **kwargs):
        raise NotImplementedError


class RandomStringTokenGenerator(BaseTokenGenerator):
    """
    Generates a random string with min and max length using os.urandom and binascii.hexlify
    """

    def __init__(self, min_length=10, max_length=50, *args, **kwargs):
        self.min_length = min_length
        self.max_length = max_length

    def generate_token(self, *args, **kwargs):
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        length = random.randint(self.min_length, self.max_length)

        return binascii.hexlify(
            os.urandom(self.max_length)
        ).decode()[0:length]

    def generate_unique_token(self, **kwargs):
        checkModel = kwargs.get("model", get_user_model())
        checkField = kwargs.get("field", "email")
        while True:
            token = self.generate_token()
            val = {
                '{0}'.format(checkField): token
            }
            if (checkModel.objects.filter(**val).count() == 0): break
        return token
