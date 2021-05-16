import logging
import re

logger = logging.getLogger()

from engine.models.externalsecrets import ExternalSecret
from engine.exceptions import ESKException


class SecretPolicy(object):
    def __init__(self, name, namespace, allow_rules, reject_rules):
        self.__name = name
        self.__namespace = namespace
        self.__allow = allow_rules or []
        self.__reject = reject_rules or []

    def get_name(self):
        return self.__name

    def check_path_allowed(self, secret: ExternalSecret):
        rejected = SecretPolicy.__rule_matches(
            secret.get_path(), secret.get_backend(), self.__reject
        )
        if rejected:
            raise ESKException(
                403,
                f"path '{secret.get_path()}' for backend '{secret.get_backend()}' is not allowed in namespace '{secret.get_namespace()}'",
            )

        allowed = SecretPolicy.__rule_matches(
            secret.get_path(), secret.get_backend(), self.__allow
        )
        if allowed:
            return True

    @classmethod
    def __rule_matches(cls, path, backend, rules):
        for rule in rules:
            if rule.get("backends") is not None and backend not in rule.get("backends"):
                continue

            if re.match(f"{ rule['pattern'] }", path):
                logger.debug(f"Allowing { path } via match with { rule['pattern'] }")
                return True

        return False
