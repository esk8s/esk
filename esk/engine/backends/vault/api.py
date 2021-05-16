import hvac
import logging

from os import environ

from engine.exceptions import ESKException
from engine.backends.vault.client import get_vault_client
from engine.backends.vault.model import VaultSecret
from engine.models.secretbindings import SecretBinding
from engine.models.secretrequest import CreateSecretRequest, UpdateSecretRequest

logger = logging.getLogger()


def get_api_instance():
    return VaultBackend()


class VaultBackend:
    def __init__(self):
        self.__client = get_vault_client()
        self.__default_mount_point = environ.get("VAULT_DEFAULT_MOUNT_POINT")

    def get_object(self, name, namespace, spec, status):
        return VaultSecret(name, namespace, spec, status)

    def create_secret(self, request: CreateSecretRequest):
        """
        Process the creation of a vaultsecrets resource
        """

        mount_point, path = request.secret.get_mount_point_and_path()

        try:
            self.__client.secrets.kv.v2.create_or_update_secret(
                path,
                secret=request.backend_values,
                mount_point=mount_point,
                cas=0,
            )
        except hvac.exceptions.InvalidRequest as e:
            raise ESKException(409, "Path already exists")

        logger.debug(f"Created secret { mount_point }/{ path } in vault.")

    def delete_secret(self, secret: VaultSecret):
        """
        Process the deletion of a vaultsecrets resource
        """

        mount_point, path = secret.get_mount_point_and_path()

        self.__client.secrets.kv.v2.delete_metadata_and_all_versions(
            path, mount_point=mount_point
        )

        logger.info(f"Deleted secret { mount_point }/{ path } in vault.")

        # policy_name = f"{ namespace }-{ name }"

        # self.__client.sys.delete_policy(policy_name)
        # logger.debug(f"Deleted policy {policy_name}")

    def move_secret(self, request: UpdateSecretRequest):
        self.delete_secret(request.old_secret)
        self.create_secret(request.secret)


    def update_secret(self, new_secret):
        """
        Process the update of a vaultsecrets resource
        """

        mount_point, path = new_secret.get_mount_point_and_path()

        self.__client.secrets.kv.v2.create_or_update_secret(
            path, secret=new_secret.get_current_values(), mount_point=mount_point
        )

        return True

    def get_secret(self, secret: VaultSecret):
        mount_point, path = secret.get_mount_point_and_path()

        try:
            values = self.__client.secrets.kv.v2.read_secret_version(
                path, mount_point=mount_point
            )["data"]["data"]
        except hvac.exceptions.InvalidPath:
            raise ESKException(404, "Secret not found in backend")

        logger.debug(f"Found secret { path } in vault.")
        return values

    def grant_access(self, bind: SecretBinding, policies: list):
        self.__client.auth.kubernetes.create_role(
            bind.get_name(),
            [bind.get_service_account()],
            [bind.get_namespace()],
            policies=policies,
        )

    def revoke_access(self, bind: SecretBinding):
        self.__client.auth.kubernetes.delete_role(bind.get_name())
