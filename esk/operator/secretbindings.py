import kopf
import logging

logger = logging.getLogger()

from controller.processors.secretbindings import SecretBindingsController

@kopf.on.create('secretbindings.esk.io')
def create_secret_binding(name, namespace, spec, patch, memo, **_):
  '''
    Process the creation of a secretbindings resource
  '''
  
  bind = SecretBindingsController.get_object(name, namespace, spec)
  memo.sb_controller.create_secret_binding(bind)

  if not bind.compare_spec(spec):
    patch['spec'] = bind.get_spec()


@kopf.on.delete('secretbindings.esk.io')
def delete_secret_binding(name, namespace, spec, memo, **_):
  '''
    Process the deletion of a secretbindings resource
  '''

  bind = SecretBindingsController.get_object(name, namespace, spec)
  memo.sb_controller.delete_secret_binding(bind)


@kopf.on.update('secretbindings.esk.io', field="spec")
def update_secret_binding(name, namespace, new, old, patch, memo, **_):
  '''
    Process the update of a secretbindings resource
  '''

  old_bind = SecretBindingsController.get_object(name, namespace, old)
  new_bind = SecretBindingsController.get_object(name, namespace, new)
  memo.sb_controller.update_secret_binding(
    old_bind,
    new_bind
  )

  if not new_bind.compare_spec(new):
    patch['spec'] = new_bind.get_spec()