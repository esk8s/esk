import kubernetes
import logging

from controller.engine import ESKEngine
from controller.exceptions import ESKException
from controller.models.externalsecrets import ExternalSecret

logger = logging.getLogger()

class ExternalSecretsController:
  def __init__(self, controller: ESKEngine):
    self.__controller = controller


  def get_secret(self, secret: dict):
    '''
      Return the secret values from the backend
    '''
    return self.__controller.get_backend_client(secret.get_backend()).get_secret(secret)


  def get_secret_spec(self, name: str, namespace: str):
    '''
      Get the CRD resource from kubernetes
    '''

    api_instance = kubernetes.client.CustomObjectsApi(self.__controller.get_backend_client('k8s'))

    try:
      return api_instance.api_instance.get_namespaced_custom_object(
        'esk.io',
        'v1alpha1',
        namespace,
        f"externalsecrets",
        name
      )
    except kubernetes.client.exceptions.ApiException:
      raise ESKException(404, f"Secret { namespace }/{ name } could not be found")


  def get_object_for_backend(self, name, namespace, backend, path, values, config = {}):
    return self.__controller.get_backend_client(backend).get_object(name, namespace, path, values, config)


  def create_secret(self, secret: ExternalSecret) -> ExternalSecret:
    '''
      Process the creation of an externalsecrets resource
    '''

    backend_client = self.__controller.get_backend_client(secret.get_backend())
    self.__controller.can_access_secret(secret)

    secret.check_can_create()

    backend_client.create_secret(secret)

    return secret


  def delete_secret(self, secret: ExternalSecret):
    '''
      Process the deletion of an externalsecrets resource
    '''

    self.__controller.can_access_secret(secret)

    self.__controller.get_backend_client(secret.get_backend()).delete_secret(secret)


  def update_secret(self, old_secret: ExternalSecret, new_secret: ExternalSecret):
    '''
      Process the update of an externalsecrets resource
    '''

    backend_client = self.__controller.get_backend_client(old_secret.get_backend())

    # when creation happens, this handler will skip updating.
    if old_secret.get_path() is None:
      return True

    self.__controller.can_access_secret(old_secret)
    self.__controller.can_access_secret(new_secret)

    __trigger_value_change = False
    old_values = old_secret.get_raw_values()
    new_values = new_secret.get_raw_values()
    real_values = None

    for k, v in new_values.items():
      if old_values.get(k) == v:
        if real_values is None:
          real_values = backend_client.get_secret(old_secret)
          if real_values is None:
            raise ESKException(500, f"Values retrieved for path { old_secret.get_path() } are None")
        
        new_values[k] = real_values[k]

    new_secret.set_real_values(new_values)
    backend_client.update_secret(__trigger_value_change, old_secret, new_secret)

    return new_secret
