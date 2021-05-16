import boto3
import logging

from engine.exceptions import ValueUnrecoverable
from engine.models.externalsecrets import ExternalSecret
from engine.models.secretrequest import CreateSecretRequest, UpdateSecretRequest
from engine.sources.model import ESKSource
from engine.exceptions import ESKException

logger = logging.getLogger()

class AwsUserAccessSource(ESKSource):
    def __init__(self, backends):
        self.__client = boto3.client("iam")


    def __check_key_exists(self, access_id):
        try:
            response = self.__client.get_access_key_last_used(
                AccessKeyId=access_id
            )
            return True
        except:
            return False

    def create_secret(self, request: CreateSecretRequest):
        self.__create(request)


    def import_secret(self, request):
        if self.__check_key_exists(request.secret.get_status().get('accessKeyID')):
            if request.backend_values.get('accessKeyID') == request.secret.get_status().get('accessKeyID'):
                request.create_in_backend = False
            else:
                raise ValueUnrecoverable(
                    f"AccessKey { request.secret.get_status().get('accessKeyID') } cannot be imported. Please recreate the secret"
                )

    def __create(self, request):
        try:
            response = self.__client.create_access_key(
                UserName=request.secret.get_spec_values()["username"]
            )["AccessKey"]
        except self.__client.exceptions.LimitExceededException as error:
            raise ESKException(409, error.response['Error']['Message'])

        request.backend_values = {
            "accessKeyID": response["AccessKeyId"],
            "secretAccessKey": response["SecretAccessKey"],
        }

        request.status["accessKeyID"] = response["AccessKeyId"]

    def update_secret(self, request: UpdateSecretRequest):
        self.delete_secret(request.old_secret)
        return self.__create(request)

    def delete_secret(self, secret):
        self.__client.delete_access_key(
            AccessKeyId=secret.get_status().get("accessKeyID"),
            UserName=secret.get_spec_values().get('username')
        )


exportedSource = AwsUserAccessSource
