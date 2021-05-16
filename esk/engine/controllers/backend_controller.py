import importlib
import logging

from os import environ

from engine.backends.k8s.api import KubernetesBackend
from engine.exceptions import ESKException

logger = logging.getLogger()

class BackendController:
    def __init__(self, backends = None):
        self.__backends = (
            environ.get("ESK_BACKENDS").split(",") if backends is None else backends
        )

        self.__clients = {"k8s": KubernetesBackend()}

        logger.info(f"Loading backends: { ','.join(self.__backends) }")

        for backend in self.__backends:
            api = importlib.import_module(f"engine.backends.{ backend }.api")

            try:
                self.__clients[backend] = api.get_api_instance()
            except ESKException as e:
                logger.error(e)
                exit(1)

        logger.info(f"Backend controller initated with backends: { ','.join(self.__backends) }")

    # def call_backend_by_name(self, name, func, params):
    #     """
    #         Call a the function "func" in the backend with the specified name, using the params
    #     """
    #     self.__clients[name][func](*params)


    # def call_backend_for_secret(self, secret, func):
    #     self.__clients[secret.get_backend()][func](secret)

    # def call_backend_for_request(self, request, func):
    #     self.__clients[request.secret.get_backend()][func](request)

    def get_backend_client(self, name):
        return self.__clients.get(name)

    def get_all_backends(self):
        return self.__clients