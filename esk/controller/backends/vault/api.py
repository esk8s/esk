import hvac
import logging

from os import environ

from controller.exceptions import ESKException
from controller.backends.vault.client import get_vault_client
from controller.backends.vault.model import VaultSecret
from controller.models.secretbindings import SecretBinding

logger = logging.getLogger()

def get_api_instance():
  return VaultBackend()


class VaultBackend:
  def __init__(self):
    self.__client = get_vault_client()
    self.__default_mount_point = environ.get('VAULT_DEFAULT_MOUNT_POINT')

  def get_object(self, name, namespace, path, values, config = {}):
    if path is None:
      mount_point = self.__default_mount_point
      path = f"{ namespace }/{ name }"
    else:
      split_path = path.split('/')
      mount_point = split_path[0]
      path = '/'.join(split_path[1:])


    return VaultSecret(name, namespace, mount_point, path, values, **config)


  def create_secret(self, secret: VaultSecret):
    '''
      Process the creation of a vaultsecrets resource
    '''

    mount_point, path = secret.get_mount_point_and_path()

    try:
      self.__client.secrets.kv.v2.create_or_update_secret(
        path,
        secret=secret.get_creation_values(),
        mount_point=mount_point,
        cas=0
      )
    except hvac.exceptions.InvalidRequest as e:
      raise ESKException(409, "Path already exists")

    logger.debug(f"Created secret { mount_point }/{ path } in vault.")

    # policy_name = f"{ namespace }-{ name }"

    # self.__client.sys.create_or_update_policy(policy_name, f"path \"{ mount_point }/{ path }\" {{\n  capabilities = [\"read\"]\n}}\n")
    # logger.debug(f"Created policy {policy_name}")

    return f"{ mount_point }/{ path }"


  def delete_secret(self, secret: VaultSecret):
    '''
      Process the deletion of a vaultsecrets resource
    '''
  
    mount_point, path = secret.get_mount_point_and_path()

    self.__client.secrets.kv.v2.delete_metadata_and_all_versions(
      path,
      mount_point=mount_point
    )

    logger.info(f"Deleted secret { mount_point }/{ path } in vault.")
    
    # policy_name = f"{ namespace }-{ name }"

    # self.__client.sys.delete_policy(policy_name)
    # logger.debug(f"Deleted policy {policy_name}")


  def update_secret(self, __trigger_value_change, old_secret, new_secret):
    '''
      Process the update of a vaultsecrets resource
    '''

    if old_secret.get_path() != new_secret.get_path():
      self.delete_secret(old_secret)
      self.create_secret(new_secret)

    elif __trigger_value_change:
      mount_point, path = new_secret.get_mount_point_and_path()

      self.__client.secrets.kv.v2.create_or_update_secret(
        path,
        secret=new_secret.get_creation_values(),
        mount_point=mount_point
      )

    return True
      

  def get_secret(self, secret: VaultSecret):
    mount_point, path = secret.get_mount_point_and_path()

    try:
      values = self.__client.secrets.kv.v2.read_secret_version(
        path,
        mount_point=mount_point
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
      policies=policies
    )


  def revoke_access(self, bind: SecretBinding):
    self.__client.auth.kubernetes.delete_role(bind.get_name())
