import logging

from os import environ

from controller.exceptions import ESKException
from controller.models.secretbindings import SecretBinding
from controller.engine import ESKEngine

logger = logging.getLogger()


class SecretBindingsController:
  def __init__(self, controller: ESKEngine):
    
    self.__is_backend_auth = (
      environ.get('AUTH_BACKEND') is not None and
      environ.get('AUTH_BACKEND').lower() == 'true'
    )

    self.__controller = controller

  @classmethod
  def get_object(cls, name, namespace, spec):
    return SecretBinding(
      name,
      namespace,
      spec.get('serviceAccount'),
      spec.get('secrets'),
      spec.get('target'),
      spec.get('template')
    )

  def get_secretbinding_spec(self, name: str, namespace: str):
    return self.__controller.get_backend_client('k8s').get_crd('secretbindings', name, namespace)


  def update_secret_binding(self, old: SecretBinding, new: SecretBinding):
    '''
      Process the update of a secretbindings resource
    '''

    self.delete_secret_binding(old)
    self.create_secret_binding(new)


  def create_secret_binding(self, bind: SecretBinding):
    '''
      Process the creation of a secretbindings resource
    '''

    if self.__is_backend_auth:
      policy_map = self.__get_backend_policies_map(bind)
      for backend, policies in policy_map:
        self.__controller.get_backend_client(backend).grant_access(bind, policies)

    else:
      self.__controller.get_backend_client('k8s').grant_access(bind)
    

  def delete_secret_binding(self, bind: SecretBinding):
    '''
      Process the deletion of a secretbindings resource
    '''

    if self.__is_backend_auth:
      backends = self.__get_backends_to_revoke_for_bind(bind)
    else:
      backends = ['k8s']
    
    for backend in backends:
      self.__controller.get_backend_client(backend).revoke_access(bind)


  def __get_backend_policies_map(self, bind: SecretBinding):
    policies = {}
    for backend in self.__backends:
      policies[backend] = []

    for s in bind.get_secrets():
      secret_backend = self.get_secret_spec(s.get('name'), bind.get_namespace()).get_backend()
      policies[secret_backend].append(f"{ bind.get_namespace() }-{ s.get('name') }")

    return policies


  def __get_backends_to_revoke_for_bind(self, bind: SecretBinding):
    revoke_backends = {}

    for s in bind.get_secrets():
      secret_backend = self.get_secret_spec(bind).get_backend()
      revoke_backends[secret_backend] = True

    return list(revoke_backends.keys())




  # def update_secret_binding(self, name, namespace, new, old):
  #   '''
  #     Process the update of a secretbindings resource
  #   '''
  #   old_binding_name = f"{ namespace }-{ old.get('spec').get('serviceAccount') }-{ old.get('name') }"
  #   new_binding_name = f"{ namespace }-{ new.get('spec').get('serviceAccount') }-{ new.get('name') }"
  #   __trigger_move = old_binding_name != new_binding_name

  #   revoke_backends = {}
  #   grant_policies = {}
  #   for backend in self.__backends:
  #     revoke_backends[backend] = False
  #     grant_policies[backend] = []

  #   for s in new.get('spec').get('secrets'):
  #     try:
  #       secret = self.get_secret_spec(s['name'], namespace)
  #     except kubernetes.client.exceptions.ApiException:
  #       raise Exception(f"Secret { namespace }/{ name } could not be found")

  #     grant_policies[secret.get('spec').get('backend')].append(f"{ namespace }-{ secret.get('name') }")

  #   if __trigger_move:
  #     for backend, should_revoke in revoke_backends.items():
  #       if should_revoke:
  #         self.__clients[backend].revoke_access(old_binding_name)

  #   for backend, policies in grant_policies.items():
  #     if len(policies) == 0:
  #       continue

  #     self.__clients.get(backend).grant_access(new.get('spec').get('serviceAccount'), old.get('name'), namespace, policies)
