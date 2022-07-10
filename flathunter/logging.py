"""Provides logger"""
import logging
import os

if os.name == 'posix':
    # provide coloring for UNIX systems
    _CYELLOW = '\033[93m'
    _CBLUE = '\033[94m'
    _COFF = '\033[0m'
else:
    _CYELLOW = ''
    _CBLUE = ''
    _COFF = ''

LOG_FORMAT = '[' + _CBLUE + '%(asctime)s' + _COFF + '|' + _CBLUE + '%(filename)-18s' + _COFF + \
                '|' + _CYELLOW + '%(levelname)-8s' + _COFF + ']: %(message)s'

logging.basicConfig(
    format=LOG_FORMAT,
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO
)

# Set logging level for "requests" module
logging.getLogger("requests").setLevel(logging.WARNING)

logger = logging.getLogger('flathunt')
