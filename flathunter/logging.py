"""Provides logger"""
import logging
import os

if os.name == 'posix':
    # provide coloring for UNIX systems
    CYELLOW = '\033[93m'
    CBLUE = '\033[94m'
    COFF = '\033[0m'
else:
    CYELLOW = ''
    CBLUE = ''
    COFF = ''

LOG_FORMAT = '[' + CBLUE + '%(asctime)s' + COFF + '|' + CBLUE + '%(filename)-18s' + COFF + \
                '|' + CYELLOW + '%(levelname)-8s' + COFF + ']: %(message)s'

logging.basicConfig(
    format=LOG_FORMAT,
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO
)

logging.getLogger("requests").setLevel(logging.WARNING)

logger = logging.getLogger('flathunt')
