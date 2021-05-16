import logging
import moment

logger = logging.getLogger()

from engine.exceptions import ESKException

class ExternalSecret(object):
    def __init__(self, name, namespace, backend, spec, status):

        self.__name = name
        self.__namespace = namespace
        self.__backend = backend

        if not self.__name:
            raise ESKException(400, "Name cannot be empty")

        if not self.__namespace:
            raise ESKException(400, "Namespace cannot be empty")

        self.__imported = spec.get("imported") or False
        self.__values = spec.get("values")
        self.__current_values = None
        self.__annotations = None
        self.__source = spec.get("source") or 'generated'
        self.__status = status or {}
        self.__spec_path = spec.get("path")
        self.__expiresAt = self.__status.get('expiresAt') or spec.get("expiresAt") or 'Never'

        if self.__expiresAt != 'Never':
            self.__expiresAt = moment(self.__expiresAt)

        self.__internal_path = self.__status.get("path") or spec.get("path") or name

        print(f"Got PATH: { self.__internal_path }")

    def as_dict(self):
        """
        Return this ExternalSecret as a dict for kubernetes
        """

        return {
            "metadata": {"name": self.__name, "namespace": self.__namespace},
            "spec": {
                "backend": self.__backend,
                "expiresAt": self.__expiresAt,
                "source": self.__source,
                "path": self.__spec_path,
                "values": self.get_spec_values(),
            },
        }

    def set_current_values(self, values):
        self.__current_values = values


    ###########
    # Getters #
    ###########
    def get_current_values(self):
        """
        Return and set the computed values spec, with generated values
        """

        return self.__current_values

    def get_name(self):
        return self.__name

    def get_namespace(self):
        return self.__namespace

    def get_spec_path(self):
        return self.__spec_path

    def get_path(self):
        return self.__internal_path

    def get_spec_values(self):
        return self.__values

    def get_spec(self):
        return self.as_dict().get("spec")

    def get_backend(self):
        return self.__backend

    def get_imported(self):
        return self.__imported

    def get_source(self):
        return self.__source

    def get_status(self):
        return self.__status

    def get_expiration_date(self):
        return self.__expiresAt