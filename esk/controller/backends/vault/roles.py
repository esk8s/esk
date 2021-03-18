import logging

logger = logging.getLogger('tool')


def create_vault_role(client, name, sas, ns, pols):
  client.auth.kubernetes.create_role(
    name,
    sas,
    ns,
    policies=pols
  )


def delete_vault_role(client):
    client.auth.kubernetes.delete_role(
      name,
      service_accounts,
      namespaces,
      policies=self.policies
    )

  # def update(self, client):
  #   self.create(client)

  # @classmethod
  # def get(self, client, name):
  #     return client.auth.kubernetes.read_role(name)

  # @classmethod
  # def list(self, client):
  #     client.auth.kubernetes.list_roles()