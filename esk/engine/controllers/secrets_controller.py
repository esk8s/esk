import importlib
import logging

from datetime import datetime
from os import environ


from engine.models.secretrequest import DeleteSecretRequest, UpdateSecretRequest, CreateSecretRequest, DeleteSecretRequest, GetSecretRequest
from engine.exceptions import ESKException
from engine.models.externalsecrets import ExternalSecret
from engine.models.secretpolicies import SecretPolicy
from engine.models.secretrequest import (
    CreateSecretRequest,
    UpdateSecretRequest
)

logger = logging.getLogger()

class ExternalSecretsController:
    def get_secret(self, request: GetSecretRequest):
        """
        Return the secret values from the backend
        """
        return request.backend_client.get_secret(request)

    def create_secret(self, request: CreateSecretRequest):
        """
        Process the creation of an externalsecrets resource
        """

        secret = request.secret

        self.__can_access_secret(secret)

        if request.secret.get_imported():
            request.backend_values = self.get_secret(request.secret)
            request.source_client.import_secret(request)
        else:
            request.source_client.create_secret(request)

        if request.create_in_backend:
            request.backend_client.create_secret(request)

        expiration = request.secret.get_expiration_date()
        request.status.update({
            "created": True,
            "path": secret.get_path(),
            "createdDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "expiresAt": expiration.strftime("%Y-%m-%dT%H:%M:%S") if not isinstance(expiration, str) else expiration
        })


    def delete_secret(self, request: DeleteSecretRequest):
        """
        Process the deletion of an externalsecrets resource
        """

        self.__.can_access_secret(request.secret)

        request.source_client.delete_secret(request.secret)
        request.backend_client.delete_secret(request.secret)


    def update_secret(self, request: UpdateSecretRequest):
        """
        Process the update of an externalsecrets resource
        """
        
        old_secret = request.old_secret
        new_secret = request.secret

        # when creation happens, this handler will skip updating.
        if old_secret.get_status() is None:
            return True

        self.__can_access_secret(old_secret)
        self.__can_access_secret(new_secret)


        # Check expiration date
        if (
            old_secret.get_spec().get("expiresAt")
            != new_secret.get_spec().get("expiresAt")
        ) or (
            old_secret.get_status().get("expiresAt") != "Never"
            and datetime.strptime(old_secret.get_status().get('createdDate'), '%Y-%m-%dT%H:%M:%S') > datetime.now()
        ):
            request.force = True

        request.source_client.update_secret(request)
        if old_secret.get_spec_path() != new_secret.get_spec_path():
            request.backend_client.move_secret(request)
        else:
            request.backend_client.update_secret(request)

        expiration = request.secret.get_expiration_date()
        request.status.update({
            "created": True,
            "path": new_secret.get_path(),
            "createdDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "expiresAt": expiration.strftime("%Y-%m-%dT%H:%M:%S") if not isinstance(expiration, str) else expiration
        })


    def __can_access_secret(self, secret: ExternalSecret):
        allowed = False

        for spec in self.__clients.get("k8s").list_crd(
            "secretpolicies", secret.get_namespace(), "v1alpha1"
        ):
            allowed = SecretPolicy(
                spec.get("name"),
                spec.get("namespace"),
                spec.get("allow"),
                spec.get("reject"),
            ).check_path_allowed(secret)

            if allowed:
                break

        if not self.__allow_by_default and not allowed:
            raise ESKException(403, "Path not allowed.")




    # def get_secret_spec(self, name: str, namespace: str):
    #     """
    #     Get the CRD resource from kubernetes
    #     """

    #     api_instance = kubernetes.client.CustomObjectsApi(
    #         self.__controller.get_backend_client("k8s")
    #     )

    #     try:
    #         return api_instance.api_instance.get_namespaced_custom_object(
    #             "esk.io", "v1alpha1", namespace, f"externalsecrets", name
    #         )
    #     except kubernetes.client.exceptions.ApiException:
    #         raise ESKException(404, f"Secret { namespace }/{ name } could not be found")