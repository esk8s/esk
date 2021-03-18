import importlib
import logging
import sys

from os import environ, path
sys.path.append(path.join(path.dirname(path.abspath(__file__)), "../"))

from controller.models.secretpolicies import SecretPolicy
from controller.models.externalsecrets import ExternalSecret
from controller.backends.k8s.api import KubernetesBackend
from controller.exceptions import ESKException

logger = logging.getLogger()


class ESKEngine:
  __clients = None
  __backends = []

  def __init__(self, backends: list = None):
    logger.info("Creating controller...")

    self.__backends = environ.get('ESK_BACKENDS').split(',') if backends is None else backends

    self.__clients = {
      'k8s': KubernetesBackend()
    }

    logger.info(f"Loading backends: { ','.join(self.__backends) }")

    for backend in self.__backends:
      api = importlib.import_module(f"controller.backends.{ backend }.api")
      
      try:
        self.__clients[backend] = api.get_api_instance()
      except ESKException as e:
        logger.error(e)
        exit(1)

    self.__allow_by_default = (
      environ.get('ALLOW_BY_DEFAULT') is not None and
      environ.get('ALLOW_BY_DEFAULT').lower() == 'true'
    )

    logger.info("Controller created.")


  def get_backend_client(self, backend):
    return self.__clients.get(backend)


  def can_access_secret(self, secret: ExternalSecret):
    allowed = False

    for spec in self.__clients.get('k8s').list_crd('secretpolicies', secret.get_namespace()):
      allowed = SecretPolicy(
        spec.get('name'),
        spec.get('namespace'),
        spec.get('allow'),
        spec.get('reject')
      ).check_path_allowed(secret)

      if allowed:
        break

    if not self.__allow_by_default and not allowed:
      raise ESKException(403, "Path not allowed.")
