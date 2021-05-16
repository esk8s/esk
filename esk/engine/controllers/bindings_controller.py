import logging

from datetime import datetime
from os import environ
from engine.models import SecretBinding, CreateBindingRequest, DeleteBindingRequest, UpdateBindingRequest, GetBindingRequest

logger = logging.getLogger()


class SecretBindingsController:
    def update_secret_binding(self, request: UpdateBindingRequest):
        """
        Process the update of a secretbindings resource
        """
        self.delete_secret_binding(request.old_bind)
        self.create_secret_binding(request.bind)

    def create_secret_binding(self, request: CreateBindingRequest):
        """
        Process the creation of a secretbindings resource
        """

        request.backend_client.grant_access(request.bind)
        request.status.update({
            "created": True,
            "createdDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        })


    def delete_secret_binding(self, request: DeleteBindingRequest):
        """
        Process the deletion of a secretbindings resource
        """
        request.backend_client.revoke_access(request.bind)
