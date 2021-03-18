import kopf
import logging

from controller.exceptions import ESKException

logger = logging.getLogger()

@kopf.on.create('externalsecrets.esk.io')
def create_secret(name, namespace, spec, memo, patch, **_):
  '''
    Process the creation of an externalsecrets resource
  '''

  try:
    original_secret = get_secret_from_spec(name, namespace, spec, memo)
    if original_secret.get_placeholder():
      return True

    created_secret = memo.s_controller.create_secret(original_secret)

    clone = created_secret.clone(True).get_spec()

    patch['spec'] = clone

  except ESKException as e:
    raise kopf.PermanentError(str(e))


@kopf.on.delete('externalsecrets.esk.io')
def delete_secret(name, namespace, spec, memo, **_):
  '''
    Process the deletion of an externalsecrets resource
  '''

  secret = get_secret_from_spec(name, namespace, spec, memo)

  try:
    memo.s_controller.delete_secret(secret)
  except ESKException as e:
    raise kopf.PermanentError(str(e))

@kopf.on.update('externalsecrets.esk.io')
def update_secret(name, namespace, memo, old, new, patch, **_):
  '''
    Process the update of an externalsecrets resource
  '''

  try:
    old_secret = get_secret_from_spec(name, namespace, old.get('spec'), memo)
    new_secret = get_secret_from_spec(name, namespace, new.get('spec'), memo)
    
    new_secret = memo.s_controller.update_secret(old_secret, new_secret)

    clone = new_secret.clone(True)
    patch['spec'] = clone.get_spec() if not clone.compare_spec(old_secret.get_spec()) else {}
  except ESKException as e:
    raise kopf.PermanentError(str(e))


def get_secret_from_spec(name, namespace, spec, memo):
  config = {}
  
  for key in ['placeholder', 'recoveryDays', 'maxVersions', 'replication']:
    if spec.get(key) is not None:
      config[key] = spec.get(key)

  return memo.s_controller.get_object_for_backend(
    name,
    namespace,
    spec.get('backend'),
    spec.get('path'),
    spec.get('values').copy(),
    config
  )