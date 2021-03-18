import kubernetes
import logging

from os import environ

from controller.exceptions import ESKException
from controller.models.secretbindings import SecretBinding

logger = logging.getLogger()

class KubernetesBackend:

  def __init__(self):
    if environ.get('KUBECONFIG') is not None:
      kubernetes.config.load_kube_config(environ.get('KUBECONFIG'))
    else:
      kubernetes.config.load_incluster_config()
    self.__client = kubernetes.client.ApiClient()
    self.__crd_api = kubernetes.client.CustomObjectsApi(self.__client)
    self.__rbac_api = kubernetes.client.RbacAuthorizationV1Api(self.__client)


  def get_crd(self, crd, name, namespace):
    try:
      return self.__crd_api.get_namespaced_custom_object(
        'esk.io',
        'v1alpha1',
        namespace,
        crd,
        name
      )
    except kubernetes.client.exceptions.ApiException as e:
      raise ESKException(e.status, e.reason)


  def list_crd(self, crd, namespace):
    try:
      return self.__crd_api.list_namespaced_custom_object(
        'esk.io',
        'v1alpha1',
        namespace,
        crd,
      ).get('items')
    except kubernetes.client.exceptions.ApiException as e:
      raise ESKException(e.status, e.reason)


  def grant_access(self, bind: SecretBinding):
    role, role_binding = bind.to_k8s_resources()
    
    try:
      self.__rbac_api.create_namespaced_role(bind.get_namespace(), role)
      self.__rbac_api.create_namespaced_role_binding(bind.get_namespace(), role_binding)
    except kubernetes.client.exceptions.ApiException as e:
      raise ESKException(e.status, e.reason)


  def revoke_access(self, bind: SecretBinding):
    try:
      self.__rbac_api.delete_namespaced_role(bind.get_name(), bind.get_namespace())
    except kubernetes.client.ApiException as e:
      if e.status != 404:
        raise ESKException(e.status, e.reason)
      else:
        logger.debug(f"Role { bind.get_name() } did not exist, skip.")

    try:
      self.__rbac_api.delete_namespaced_role_binding(bind.get_name(), bind.get_namespace())
    except kubernetes.client.ApiException as e:
      if e.status != 404:
        raise ESKException(e.status, e.reason)
      else:
        logger.debug(f"Role binding { bind.get_name() } did not exist, skip.")

