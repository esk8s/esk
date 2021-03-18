
from controller.models.externalsecrets import ExternalSecret

class AWSSecret(ExternalSecret):

  def __init__(self, name, namespace, path, values, placeholder = False, recoveryDays = 0):
    super().__init__(name, namespace, "aws", placeholder, path, values)

    self.__recovery_days = recoveryDays


  def get_backend(self):
    return "aws"


  def should_delete_instantly(self):
    return self.__recovery_days == 0


  def get_recovery_days(self):
    return self.__recovery_days