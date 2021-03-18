import kubernetes

from flask.globals import current_app
from os import environ

class ESKProcessor:
  def __init__(self, controller):
    self.__controller = controller

    self.__k8s_host = environ.get('KUBERNETES_PORT_443_TCP_ADDR')
    if environ.get('K8S_CA_CERT'):
      self.__k8s_ca_cert = environ.get('K8S_CA_CERT')
    else:
      self.__k8s_ca_cert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'

  def get_k8s_conf_for_request(self, auth):
      configuration = kubernetes.client.Configuration()
      configuration.api_key["authorization"] = auth

      configuration.host = f"https://{ self.__k8s_host }"
      configuration.ssl_ca_cert = self.__k8s_ca_cert

      return configuration


  def process_secret_read(self, auth, name, namespace):
      '''
        Uses provided credentials
      '''

      with kubernetes.client.ApiClient(self.get_k8s_conf_for_request(auth)) as api_client:
        api_instance = kubernetes.client.CustomObjectsApi(api_client)

      try:
        secret_desc = api_instance.get_namespaced_custom_object(
          'esk.io',
          'v1alpha1',
          namespace,
          'externalsecrets',
          name
        )
      except kubernetes.client.exceptions.ApiException as e:
        return e.status, e.reason

      secret = self.__controller.get_object_for_backend(
        name,
        namespace,
        secret_desc.get('spec').get('backend'),
        secret_desc.get('spec').get('path'),
        secret_desc.get('spec').get('values')
      )
      values = self.__controller.get_secret(secret)

      return 200, values
