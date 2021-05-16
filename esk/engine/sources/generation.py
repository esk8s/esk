import logging
import moment
import random
import re
import string

from engine.models.externalsecrets import ExternalSecret
from engine.models.secretrequest import CreateSecretRequest, UpdateSecretRequest
from engine.sources.model import ESKSource
from engine.exceptions import ESKException

logger = logging.getLogger()


class GenerationSource(ESKSource):
    def __check_can_create(self, secret):
        if (
            not isinstance(secret.get_spec_values(), dict)
            or len(secret.get_spec_values().keys()) == 0
        ):
            raise ESKException(
                500,
                f"Failed to create: values not a valid dict: { secret.get_spec_values() }",
            )


    def import_secret(self, request):
        if request.backend_values is not None:
            request.create_in_backend = False
            return

    def create_secret(self, request: CreateSecretRequest):
        self.__check_can_create(request.secret)

        request.backend_values = transform_values(request.secret.get_spec_values())

    def update_secret(self, request: UpdateSecretRequest):        
        old_values = request.old_secret.get_spec_values()
        new_values = request.secret.get_spec_values()

        original_keys = []

        if request.force:
            generated_values = new_values.copy()
        else:
            generated_values = {}
            for k, v in new_values.items():
                if k in old_values:
                    original_keys.append(k)
                else:
                    generated_values[k] = v

        if len(generated_values) == 0:
            request.create_in_backend = False
            return

        request.backend_values = transform_values(generated_values)

        if len(original_keys) > 0: # update needs to be done
            current_values = request.backend_client.get_secret(request.old_secret)
            if current_values is None:
                raise ESKException(
                    500,
                    f"Values retrieved for path { request.old_secret.get_path() } are None",
            )

            for key in original_keys:
                request.backend_values[key] = current_values[key]


    def delete_secret(self, secret: ExternalSecret):
        pass



def transform_values(values):
    new_values = {}
    for k, v in values.items():
        match = None
        for regex, fn in __VALUES_OPERATORS.items():
            match = re.match(regex, v)
            if match:
                new_values[k] = fn(match)
                break
        
        if not match:
            new_values[k] = v

    return new_values

def get_random_string(match):
    length = match.group(1) or 32
    chars = string.ascii_letters + string.digits
    result_str = "".join(random.choice(chars) for _ in range(length))

    return result_str

__VALUES_OPERATORS = {"^gen(\[[0-9]{1,4}\]$)*": get_random_string}


exportedSource = GenerationSource