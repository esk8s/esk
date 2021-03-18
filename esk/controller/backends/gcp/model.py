
from controller.models.externalsecrets import ExternalSecret

class GCPSecret(ExternalSecret):

  def __init__(self, name, namespace, path, values, placeholder = False, replication = None):
    super().__init__(name, namespace, "gcp", placeholder, path, values)

    self.__replication = replication or {'automatic': {}}


  def get_replication(self):
    return self.__replication