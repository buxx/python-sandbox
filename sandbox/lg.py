# coding: utf-8
import sys

import logging


def get_logger(level=logging.ERROR, name: str = None):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


lg = get_logger()
