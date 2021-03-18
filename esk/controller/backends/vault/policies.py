import logging

logger = logging.getLogger('tool')


def create_vault_policy(client, name, rules):
    policy_text = ""

    for item in rules:
        caps = item["capabilities"] if "capabilities" in item else ["read"]
        policy_text += (
            f"path \"{item['path']}\" {{\n  capabilities = {caps}\n}}\n".replace(
                "'", '"'
            )
        )

    logger.debug(f"Creating policy {name}")
    client.sys.create_or_update_policy(name, policy_text)


def delete_vault_policy(client, name):
  client.sys.delete_policy(name)


@classmethod
def list(self, client):
  client.sys.list_policies()