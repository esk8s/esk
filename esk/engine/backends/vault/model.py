from os import environ

from engine.exceptions import ESKException
from engine.models.externalsecrets import ExternalSecret


class VaultSecret(ExternalSecret):
    def __init__(self, name, namespace, spec, status={}):

        super().__init__(name, namespace, "vault", spec, status)

        split_path = self.__status.get("path").split("/")
        if len(split_path) > 1:
            self.__mount_point = split_path[0]
            self.spec_path = "/".join(split_path[1:])
        else:
            self.__mount_point = self.__default_mount_point
            self.spec_path = name

        self.__max_versions = spec.get("maxVersions") or 10

    def get_mount_point_and_path(self):
        return self.__mount_point, super().get_spec_path()

    def get_path(self):
        return f"{ self.__mount_point }/{ super().get_path() }"

    def as_dict(self):
        ext = super().as_dict()
        ext.update({"max_versions": self.__max_versions})

        return ext

    def get_backend(self):
        return "vault"
