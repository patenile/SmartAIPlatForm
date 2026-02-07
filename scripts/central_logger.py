#!/usr/bin/env python3
"""
Centralized logger for all SmartAIPlatform scripts.
"""
import logging
import sys

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"

# Singleton logger instance
_logger = None

def get_logger(name="SmartAIPlatform", debug=False):
    global _logger
    if _logger is not None:
        return _logger
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.propagate = False
    _logger = logger
    return logger
