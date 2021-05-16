import requests

from os import environ

from engine.exceptions import ValueUnrecoverable
from engine.models.externalsecrets import ExternalSecret
from engine.models.secretrequest import CreateSecretRequest, UpdateSecretRequest
from engine.sources.model import ESKSource


class GitlabAccessTokenSource(ESKSource):
    def __init__(self, backends):
        if environ.get("GITLAB_SECRET") is not None:
            if environ.get("GITLAB_SECRET_BACKEND") is None:
                for name in list(backends.keys()):
                    if name != 'k8s':
                        backend_name = name
                        break
            else:
                backend_name = environ.get("GITLAB_SECRET_BACKEND")

            self.__token = backends.get(backend_name).get_secret_from_path(
                environ.get("GITLAB_SECRET")
            )
        else:
            with open(environ.get("GITLAB_TOKEN_PATH"), "r") as f:
                self.__token = f.read().strip()

        self.__url = f"{ environ.get('GITLAB_SCHEME') or 'https' }://{ environ.get('GITLAB_API_URL') }"
        self.__headers = {"PRIVATE-TOKEN": self.__token}

    def __check_key_exists(self, user_id, token_name):
        response = requests.get(
            f"{ self.__url }/personal_access_tokens?user_id={ user_id }",
            headers=self.__headers,
        ).json()

        for key in response:
            if key.get('name') == token_name:
                return True

        return False

    def get_secret(self, secret: ExternalSecret):
        raise ValueUnrecoverable(
            f"AccessKey { secret.get_spec_values().get('accessKeyID') } cannot be recovered"
        )


    def import_secret(self, request):
        user_id_resp = requests.get(
            f"{ self.__url }/users?username={ request.secret.get_spec_values()['username'] }"
        )
        user_id = user_id_resp.json()[0].get("id")

        if self.__check_key_exists(
            user_id,
            request.secret.get_spec_values()['tokenName']
        ):
            raise ValueUnrecoverable(
                f"Token { request.secret.get_status().get('tokenName') } cannot be imported. Please recreate the secret"
            )

    def create_secret(self, request: CreateSecretRequest):
        user_id_resp = requests.get(
            f"{ self.__url }/users?username={ request.secret.get_spec_values()['username'] }"
        )

        user_id = user_id_resp.json()[0].get("id")
        self.__create_gitlab_token(user_id, request.secret)


    def __create_gitlab_token(self, user_id, request: CreateSecretRequest):
        plugin_config = request.secret.get_spec_values()

        req_body = {
            "user_id": user_id,
            "name": plugin_config["tokenName"],
            "scopes": plugin_config["scopes"],
        }

        if request.secret.get_spec().get("expiresAt") is not None:
            req_body["expiresAt"] = request.secret.get_spec().get("expiresAt")

        response = requests.post(
            f"{ self.__url }/users/{ user_id }/personal_access_tokens",
            json=req_body,
            headers=self.__headers,
        ).json()

        request.backend_values = {
            "token": response.get("token"),
        }

        request.status.update({
            "userID": user_id
        })


    def update_secret(self, request: UpdateSecretRequest):
        self.delete_secret(request.secret)

        return self.__create_gitlab_token(
            request.old_secret.get_status().get("user_id"), request
        )

    def delete_secret(self, secret):
        requests.delete(
            f"{ self.__url }/personal_access_tokens",
            json={"id": secret.get_status().get("token_id")},
            headers=self.__headers,
        )


exportedSource = GitlabAccessTokenSource
