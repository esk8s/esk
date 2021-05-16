import importlib
import logging

from os import environ

from engine.models import ExternalSecret, SecretBinding, CreateSecretRequest, UpdateSecretRequest, DeleteSecretRequest, GetSecretRequest, CreateBindingRequest, GetBindingRequest, UpdateBindingRequest, DeleteBindingRequest
from engine.controllers import BackendController, ExternalSecretsController, SecretBindingsController

logger = logging.getLogger()

class ESKEngine(object):
    _backends = None

    def __init__(self):
        self._backends = BackendController()

    def get_object_spec(self, name, namespace, kind, version = 'v1beta1'):
        return self._backends['k8s'].get_object_spec(name, namespace, kind, version)

    def get_object_for_backend(self, name, namespace, spec, status={}):
        return self._backends.get_backend_client(spec.get("backend")).get_object(
            name, namespace, spec, status
        )

class ESKWriterEngine(ESKEngine):
    def __init__(self):
        super().__init__()
        self.__secrets_controller = ExternalSecretsController()
        self.__binds_controller = SecretBindingsController()
        self.__sources = {}

        self.__allow_by_default = (
            environ.get("ALLOW_BY_DEFAULT") is not None
            and environ.get("ALLOW_BY_DEFAULT").lower() == "true"
        )

        source_names = ['generation', 'aws_user_access', 'gitlab_access_token']
        if environ.get("ESK_PLUGINS") is not None:
            source_names += environ.get("ESK_PLUGINS").split(",")

        for source in source_names:
            try:
                self.__sources[source] = importlib.import_module(f"base.sources.{ source }").exportedSource(self.__controller.get_all_backends())
                logger.info(f"Source { source } loaded")
            except ModuleNotFoundError:
                logger.info(f"Source { source } not found.")

    # Secrets
    def create_secret(self, secret: ExternalSecret):
        request = self.__new_request(secret, CreateSecretRequest)
        self.__secrets_controller.create_secret(request)

        return request

    def update_secret(self, old_secret: ExternalSecret, new_secret: ExternalSecret):
        request = UpdateSecretRequest(old_secret, new_secret)
        request.backend_client = self._backends.get_backend_client(old_secret.get_backend())
        request.source_client = self.__sources[old_secret.get_source()]

        self.__secrets_controller.update_secret(request)
        return request

    def delete_secret(self, secret: ExternalSecret):
        request = self.__new_request(secret, DeleteSecretRequest)
        self.__secrets_controller.delete_secret(request)
        return request

    def __new_request(self, secret: ExternalSecret, obj):
        request = obj(secret)
        request.backend_client = self._backends.get_backend_client(secret.get_backend())
        request.source_client = self.__sources[secret.get_source()]

        return request

    # binds
    def create_bind(self, bind: SecretBinding):
        request = self.__new_request(bind, CreateBindingRequest)
        self.__binds_controller.create_bind(request)

        return request

    def update_bind(self, old_bind: SecretBinding, new_bind: SecretBinding):
        request = UpdateBindingRequest(old_bind, new_bind)
        request.backend_client = self._backends.get_backend_client('k8s')

        self.__binds_controller.update_bind(request)
        return request

    def delete_bind(self, bind: SecretBinding):
        request = self.__new_request(bind, DeleteBindingRequest)
        self.__binds_controller.delete_bind(request)
        return request

    def __new_request(self, bind: SecretBinding, obj):
        request = obj(bind)
        request.backend_client = self._backends.get_backend_client('k8s')

        return request



class ESKReaderEngine(ESKEngine):
    def __init__(self):
        super().__init__()
        self.__secrets_controller = ExternalSecretsController() # reader mode
        self.__binds_controller = SecretBindingsController()

    def get_secret(self, secret: ExternalSecret):
        request = GetSecretRequest(secret)
        request.backend_client = self._backends.get_backend_client(secret.get_backend())

        return self.__secrets_controller.get_secret(request)

    def get_bind(self, bind: SecretBinding):
        request = GetBindingRequest(bind)
        request.backend_client = self._backends.get_backend_client('k8s')

        return self.__binds_controller.get_secret(request)
