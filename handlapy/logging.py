import logging
import json
import os


handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s:\t  %(asctime)s [%(threadName)s] %(name)s::%(funcName)s %(message)s'))


def debugd(self, dct):
    s = json.dumps(dct, indent=2)
    self.debug(os.linesep + s)


logging.Logger.debugd = debugd


def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.handlers = [handler]
    return logger
