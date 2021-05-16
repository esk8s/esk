from engine.models.externalsecrets import ExternalSecret


class GCPSecret(ExternalSecret):
    def __init__(self, name, namespace, spec, status={}):
        super().__init__(name, namespace, "gcp", spec, status)

        self.__replication = spec.get("replication") or {"automatic": {}}

    def get_replication(self):
        return self.__replication
