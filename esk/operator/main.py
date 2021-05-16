import asyncio
import logging
import kopf
import sys

from os import path

sys.path.append(path.join(path.dirname(path.abspath(__file__)), "../"))

from engine.main import ESKWriterEngine
from engine.models import SecretBinding

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@kopf.on.startup()
def configure(memo, **_):
    logger.info("Starting up the operator")

    memo.engine = ESKWriterEngine()

    logger.info("Operator started successfully")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


@kopf.on.create("externalsecrets.esk.io")
@kopf.on.delete("externalsecrets.esk.io")
@kopf.on.update("externalsecrets.esk.io")
def secret(name, namespace, memo, body, reason, **kwargs):
    if reason == 'create':
        request = memo.requests.create_secret(
            memo.engine.get_object_from_backend(name, namespace, body.get('spec'))
        )

    elif reason == 'update':
        request = memo.engine.update_secret(
            memo.engine.get_object_from_backend(
                name, namespace, kwargs.get("old").get('spec'), kwargs.get('status').get('secret')
            ),
            memo.engine.get_object_from_backend(
                name, namespace, kwargs.get("new").get('spec')
            )
        )
    elif reason == 'delete':
        memo.requests.delete_secret(
            memo.engine.get_object_from_backend(name, namespace, kwargs.get('spec'), body.get('status').get('secret'))
        )
        return

    return request.status


@kopf.on.create("secretbindings.esk.io")
@kopf.on.delete("secretbindings.esk.io")
@kopf.on.update("secretbindings.esk.io")
def binding(name, namespace, memo, body, reason, **kwargs):
    if reason == 'create':
        request = memo.engine.create_bind(
            SecretBinding(name, namespace, body.get('spec'))
        )

    elif reason == 'update':
        request = memo.engine.update(
            
            SecretBinding(
                name, namespace, kwargs.get("old").get('spec'), kwargs.get('status').get('binding')
            ),
            SecretBinding(
                name, namespace, kwargs.get("new").get('spec')
            )
        )
    elif reason == 'delete':
        memo.engine.delete_bind(
            SecretBinding(name, namespace, kwargs.get('spec'), memo, body.get('status').get('binding'))
        )
        return

    return request.status
