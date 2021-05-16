from engine.models import SecretBinding

class BindingRequest:
    backend_values = None
    backend_client = None
    status = {}
    bind = None
    source_client = None

    def __init__(self, bind: SecretBinding):
        self.bind = bind


class UpdateBindingRequest(BindingRequest):
    unrecoverable = False
    imported_values = None


class CreateBindingRequest(BindingRequest):
    unrecoverable = False
    old_bind = False
    force = False

    def __init__(self, old_bind: SecretBinding, new_binding: SecretBinding, force = False):
        self.old_bind = old_bind
        self.bind = new_binding
        self.force = force
        self.status = old_bind.get_status() or {}


class GetBindingRequest(BindingRequest):
    pass


class DeleteBindingRequest(BindingRequest):
    pass