import boto3
import json
import logging

from datetime import datetime

from engine.backends.aws.model import AWSSecret
from engine.exceptions import ESKException
from engine.models.secretrequest import CreateSecretRequest, UpdateSecretRequest

logger = logging.getLogger()

def get_api_instance():
    return AWSBackend()


class AWSBackend:
    def __init__(self):
        self.__client = boto3.client("secretsmanager")

    def get_object(self, name, namespace, spec, status):
        return AWSSecret(name, namespace, spec, status)

    def create_secret(self, request: CreateSecretRequest):
        """
        Process the creation of an awssecrets resource
        """

        try:
            self.__client.create_secret(
                Name=request.secret.get_path(),
                SecretString=json.dumps(request.backend_values),
            )
        except self.__client.exceptions.ResourceExistsException:
            raise ESKException(409, "Path already exists")
        except self.__client.exceptions.InvalidRequestException as e:
            if 'scheduled for deletion' in e.response['Error']['Message']:
                self.__client.restore_secret(SecretId=request.secret.get_path())
                self.__client.put_secret_value(
                    SecretId=request.secret.get_path(),
                    SecretString=json.dumps(request.backend_values),
                )
            else:
                raise e
        except Exception as e:
            raise ESKException(500, e)

    def delete_secret(self, secret: AWSSecret):
        """
        Process the deletion of an awssecrets resource
        """

        try:
            if secret.should_delete_instantly():
                logger.info("delete instantly")
                self.__client.delete_secret(
                    ForceDeleteWithoutRecovery=True, SecretId=secret.get_path()
                )
            else:
                logger.info(f"delete after {secret.get_recovery_days()}")
                self.__client.delete_secret(
                    RecoveryWindowInDays=secret.get_recovery_days(),
                    SecretId=secret.get_path(),
                )
        except self.__client.exceptions.ResourceNotFoundException:
            logger.info("Object not found, so deletion is considered successful")
            return True
        except self.__client.exceptions.InvalidRequestException as e:
            raise ESKException(500, e.getMessage())

    def move_secret(self, request: UpdateSecretRequest):
        self.delete_secret(request.old_secret)
        self.create_secret(request)

    def update_secret(self, request: UpdateSecretRequest):
        """
        Process the update of a vaultsecrets resource
        """
        logger.info(f"Writing to: {request.secret.get_path()}")
        try:
            self.__client.put_secret_value(
                SecretId=request.secret.get_path(),
                SecretString=json.dumps(request.backend_values),
            )
        except self.__client.exceptions.ResourceNotFoundException:
            raise ESKException(500, f"Path {request.secret.get_path()} not found, so can't update")

    def get_secret(self, secret: AWSSecret):
        return json.loads(
            self.__client.get_secret_value(SecretId=secret.get_path()).get(
                "SecretString"
            )
        )

    def get_secret_from_path(self, path: str):
        return self.__client.get_secret_value(SecretId=path).get("SecretString")

    def get_secret(self, secret: AWSSecret):
        return json.loads(
            self.__client.get_secret_value(SecretId=secret.get_path()).get(
                "SecretString"
            )
        )

    # def grant_access(self, s_account, name, namespace):
    #   pol = aws_policy_template.copy()
    #   pol['Statement']['Principal']['AWS'] += f"{ self.__aws_account_id }:{ s_account }"

    #   self.__client.put_resource_policy(
    #     SecretId=name,
    #     ResourcePolicy=json.dumps(pol),
    #     BlockPublicPolicy=True|False
    #   )

    # def revoke_access(self, s_account, name, namespace):
    #   pass
    #   # pol = aws_policy_template.copy()
    #   # pol['Statement']['Principal']['AWS'] += f"{ __aws_account_id }:{ s_account }"

    #   # self.__client.put_resource_policy(
    #   #   SecretId=name,
    #   #   ResourcePolicy=json.dumps(pol),
    #   #   BlockPublicPolicy=True|False
    #   # )
