import sys

from os import path, environ

sys.path.append(path.join(path.dirname(path.abspath(__file__)), "../"))

environ["ESK_BACKENDS"] = "vault,gcp,aws"
environ["VAULT_DEFAULT_MOUNT_POINT"] = "test"

## Requires the env vars:
# - VAULT_ADDR, VAULT_TOKEN
# - GCP_PROJECT_ID


from engine.main import get_controllers

s_controller, sb_controller = get_controllers()

secrets = [
    {
        "name": "test-vault",
        "namespace": "test",
        "spec": {"backend": "vault", "values": {"test": "gen"}},
    },
    {
        "name": "test-aws",
        "namespace": "test",
        "spec": {"backend": "aws", "values": {"test": "gen"}},
    },
    {
        "name": "test-gcp",
        "namespace": "test",
        "spec": {"backend": "gcp", "values": {"test": "gen"}},
    },
]


def test_secret(test_secret):
    """
    Process the creation of an externalsecrets resource
    """

    old_secret = memo.engine.get_object_from_backend(
        test_secret.get("name"),
        test_secret.get("namespace"),
        test_secret.get("spec"),
    )

    new_spec = test_secret.copy()
    new_spec["spec"]["path"] = old_secret.get_path() + "-moved"

    new_secret = memo.engine.get_object_from_backend(
        new_spec.get("name"),
        new_spec.get("namespace"),
        new_spec.get("spec"),
    )

    created_path = s_controller.create_secret(old_secret)
    if created_path.get_path() != old_secret.get_path():
        raise Exception(
            f"Path does not match. Created with { created_path.get_path() } but expected {old_secret.get_path()}"
        )

    retrieved_before_move = s_controller.get_secret(old_secret)
    new_secret.set_real_values(retrieved_before_move)

    print("Moving to : " + new_secret.get_path())
    s_controller.update_secret(old_secret, new_secret)

    retrieved_after_move = s_controller.get_secret(new_secret)
    if retrieved_after_move.get("test") is None:
        print(retrieved_after_move)
        raise Exception("Could not correctly retrieve the value")
    elif retrieved_after_move.get("test") != retrieved_before_move.get("test"):
        print(retrieved_before_move)
        print(retrieved_after_move)
        raise Exception("Values do not match after move")

    s_controller.delete_secret(new_secret)


def memo.engine.get_object_from_backend(name, namespace, spec):
    config = {}

    for key in ["placeholder", "recoveryDays", "maxVersions", "replication"]:
        if spec.get(key) is not None:
            config[key] = spec.get(key)

    return s_controller.get_object_for_backend(name, namespace, spec)


for s in secrets:
    test_secret(s)
