from controller.engine import ESKEngine
from controller.processors.externalsecrets import ExternalSecretsController
from controller.processors.secretbindings import SecretBindingsController


def get_controllers():
  main_controller = ESKEngine()

  return (
    ExternalSecretsController(main_controller),
    SecretBindingsController(main_controller)
  )