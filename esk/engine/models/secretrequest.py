from engine.models import ExternalSecret

class SecretRequest:
    backend_values = None
    backend_client = None
    status = {}
    secret = None
    create_in_backend = False
    source_client = None

    def __init__(self, secret: ExternalSecret):
        self.secret = secret


class CreateSecretRequest(SecretRequest):
    unrecoverable = False
    imported_values = None


class UpdateSecretRequest(SecretRequest):
    unrecoverable = False
    old_secret = False
    force = False

    def __init__(self, old_secret: ExternalSecret, new_secret: ExternalSecret, force: bool = False):
        self.old_secret = old_secret
        self.secret = new_secret
        self.force = force
        self.status = old_secret.get_status() or {}


class GetSecretRequest(SecretRequest):
    pass


class DeleteSecretRequest(SecretRequest):
    pass