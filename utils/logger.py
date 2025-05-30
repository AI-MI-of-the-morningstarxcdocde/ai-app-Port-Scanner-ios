"""
Logger Utility Module
Author: morningstar
Poster: morningstar's Ethical Hacking Suite
Description: Provides logging setup and logger instance for the project
"""

import logging

_logger = None


def setup_logger():
    global _logger
    if _logger is None:
        _logger = logging.getLogger("AdvancedPortScanner")
        _logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        _logger.addHandler(ch)


def get_logger():
    global _logger
    if _logger is None:
        setup_logger()
    return _logger
