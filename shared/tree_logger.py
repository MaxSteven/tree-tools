#!/usr/bin/env python

import sys
import logging


def tree_logger(purge_log):
    # Logging
    logger = logging.getLogger('TreeLogger')
    hdlr = logging.FileHandler(purge_log)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    # Logging to stdout
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
