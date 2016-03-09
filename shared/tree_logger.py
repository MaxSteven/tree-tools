#!/usr/bin/env python

import sys
import logging


def tree_logger(log_filepath):
    # Logging
    logger = logging.getLogger('TreeLogger')
    hdlr = logging.FileHandler(log_filepath)
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
