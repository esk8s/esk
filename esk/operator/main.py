import asyncio
import logging
import kopf
import sys

from os import path
sys.path.append(path.join(path.dirname(path.abspath(__file__)), "../"))

from controller.main import get_controllers

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

@kopf.on.startup()
def configure(memo, **_):
  logger.info("Starting up the operator")

  memo.s_controller, memo.sb_controller = get_controllers()

  logger.info("Operator started successfully")

  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
