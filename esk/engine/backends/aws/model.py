from engine.models.externalsecrets import ExternalSecret


class AWSSecret(ExternalSecret):
    def __init__(self, name, namespace, spec, status={}):
        super().__init__(name, namespace, "aws", spec, status)

        self.__recovery_days = spec.get("recoveryDays") or 0

    def get_backend(self):
        return "aws"

    def should_delete_instantly(self):
        return self.__recovery_days == 0

    def get_recovery_days(self):
        return self.__recovery_days
