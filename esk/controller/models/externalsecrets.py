import logging
import random
import re
import string

logger = logging.getLogger()

from controller.exceptions import ESKException

def get_random_string(match):
  length = match.group(1) or 32
  chars = string.ascii_letters + string.digits
  result_str = "".join(random.choice(chars) for _ in range(length))

  return result_str


class ExternalSecret(object):
  __VALUES_OPERATORS = {
    "^gen(\[[0-9]{1,4}\]$)*": get_random_string
  }

  def __init__(self, name, namespace, backend, placeholder, path, values):
    self.__name = name
    self.__namespace = namespace
    self.__backend = backend

    if not self.__name:
      raise ESKException(400, "Name cannot be empty")

    if not self.__namespace:
      raise ESKException(400, "Namespace cannot be empty")

    self.__placeholder = placeholder
    self.__values = values if values is not None else {}
    self.__real_values = None
    self.__annotations = None
    self.__masked_values = {}
    self.__set_masked_values()

    if path is None:
      self.__path = f"{ self.__namespace }-{ self.__name }"
    else:
      self.__path = path


  def check_can_create(self):
    if not self.__path:
      raise ESKException(500, "Secrets require a valid path")

    if not isinstance(self.__values, dict) or len(self.__values.keys()) == 0:
      raise ESKException(500, f"Failed to create: values not a valid dict: { self.__values}")


  def as_dict(self):
    '''
      Return this ExternalSecret as a dict for kubernetes
    '''

    return {
      'metadata': {
        'name': self.__name,
        'namespace': self.__namespace
      },
      'spec': {
        'backend': self.__backend,
        'path': self.get_path(),
        'values': self.get_raw_values()
      }
    }


  def set_real_values(self, values):
    self.__real_values = values


  def __set_masked_values(self):
    '''
      Mask the values spec
    '''
    self.__masked_values = self.__values.copy()

    for k, val in self.__values.items():
      matched = False

      for regex in list(self.__VALUES_OPERATORS.keys()):
        compiled = re.compile(regex)
        match = compiled.match(val)
        if match:
          matched = True
          break
      
      if not matched:
        self.__masked_values[k] = "[[MASKED]]"


  def get_creation_values(self):
    '''
      Return and set the computed values spec, with generated values
    '''
    values = self.__values.copy()

    if self.__real_values is not None:
      values.update(self.__real_values)

    for k, v in values.items():
      for regex, fn in self.__VALUES_OPERATORS.items():
        match = re.match(regex, v)
        if match:
          values[k] = fn(match)
          break

    self.set_real_values(values)
    return values


  def compare_spec(self, spec):
    '''
      Compare a spec with self.spec, return true if the same
    '''
    for k, v in self.__values.items():
      if spec.get('values')[k] != v:
        return False

    return self.__path == spec.get('path')


  def clone(self, masked = True):
    return self.__class__(
      self.__name,
      self.__namespace,
      self.get_path(),
      self.__values if not masked else self.__masked_values
    )


  ###########
  # Getters #
  ###########
  def get_masked_values(self):
    return self.__masked_values


  def get_name(self):
    return self.__name


  def get_namespace(self):
    return self.__namespace


  def get_path(self):
    return self.__path


  def get_raw_values(self):
    return self.__values


  def get_spec(self):
    return self.as_dict().get('spec')


  def get_backend(self):
    return self.__backend

  
  def get_placeholder(self):
    return self.__placeholder