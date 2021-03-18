import json

from os import environ
from google.cloud import secretmanager
from google import api_core

from controller.exceptions import ESKException
from controller.backends.gcp.model import GCPSecret

def get_api_instance():
  return GCPBackend()

class GCPBackend:
  def __init__(self):
    self.__client = secretmanager.SecretManagerServiceClient()
    self.__project_id = f"{ environ.get('GCP_PROJECT_ID') }"


  def get_object(self, name, namespace, path, values, config):
    return GCPSecret(name, namespace, path, values, **config)
  

  def create_secret(self, secret: GCPSecret):
    '''
      Process the creation of an gcpsecrets resource
    '''

    # Build a dict of settings for the secret
    secret_metadata = { 'replication': secret.get_replication() }

    # Create the secret
    try:
      self.__client.create_secret(
        secret_id=secret.get_path(),
        parent=f"projects/{ self.__project_id }",
        secret=secret_metadata
      )
    except api_core.exceptions.AlreadyExists as e:
      raise ESKException(409, "Path already exists")

    self.__add_secret_version(secret)


  def get_secret(self, secret: GCPSecret) -> dict:
    '''
      Get the secret from the backend and return as json
    '''

    path = self.__client.secret_path(self.__project_id, secret.get_path())

    response = self.__client.access_secret_version(request={"name": f"{ path }/versions/latest" })
    return json.loads(response.payload.data.decode("UTF-8"))


  def delete_secret(self, secret: GCPSecret):
    '''
      Process the deletion of an gcpsecrets resource
    '''
    path = self.__client.secret_path(self.__project_id, secret.get_path())

    self.__client.delete_secret(request={"name": path})


  def update_secret(self, __trigger_value_change: bool, old_secret: GCPSecret, new_secret: GCPSecret):
    '''
      Process the update of an gcpsecrets resource
    '''

    if old_secret.get_path() != new_secret.get_path():
      self.delete_secret(old_secret)
      self.create_secret(new_secret)

    elif __trigger_value_change:
      self.__add_secret_version(new_secret)


  def __add_secret_version(self, secret: GCPSecret):
      '''
      Create a new version for the secret using the new values
      '''

      response = self.__client.add_secret_version(
        request = {
          "parent": self.__client.secret_path(self.__project_id, secret.get_path()),
          "payload": {
            "data": json.dumps(secret.get_creation_values()).encode('utf-8')
          }
        }
      )

      # Print the new secret version name.
      print(f'Added secret version: {response.name}')


  def grant_access(self, s_account, name, namespace, policies):
      '''
      Grant the given member access to a secret.
      '''

      resource_name = self.__client.secret_path(self.__project_id, f"{ namespace }-{ name }")

      policy = self.__client.get_iam_policy(request={"resource": resource_name})
      policy.bindings.add(role="roles/secretmanager.secretAccessor", members=[s_account])
      self.__client.set_iam_policy(request={"resource": resource_name, "policy": policy})

      # Print data about the secret.
      print("Updated IAM policy on {}".format(name))


  def revoke_access(self, s_account, name, namespace):
      '''
      Revoke the given member access to a secret.
      '''
    
      resource_name = self.__client.secret_path(self.__project_id, f"{ namespace }-{ name }")

      policy = self.__client.get_iam_policy(request={"resource": resource_name})

      # Remove the given member's access permissions.
      accessRole = "roles/secretmanager.secretAccessor"
      for b in list(policy.bindings):
        if b.role == accessRole and s_account in b.members:
          b.members.remove(s_account)

      new_policy = self.__client.set_iam_policy(request={"resource": resource_name, "policy": policy})

      # Print data about the secret.
      print("Updated IAM policy on {}".format(resource_name))
