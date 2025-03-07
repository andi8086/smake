import sys
import traceback
import argparse
import logging
import yaml
from build_tree import *

if __name__ != '__main__':
        sys.exit(-1)

PROGNAME = 'smake'
VERSION = '0.1'
DESCRIPTION = 'Super Make - v{} - ' \
        'A build tool with focus on embedded projects' \
        .format(VERSION)

EPILOG = 'Because everything sucks.'

logger = logging.getLogger(PROGNAME)
logging.basicConfig(level = logging.INFO,
     format='%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s',
     datefmt='%Y-%m-%d %H:%M:%S')

logging.addLevelName(logging.WARNING,
        "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName(logging.ERROR,
        "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))

parser = argparse.ArgumentParser(
        prog = PROGNAME,
        description = DESCRIPTION,
        epilog = EPILOG)

args = parser.parse_args()

try:
        tree = build_tree(logger)
        tree.build()

except Exception as err:
        logger.exception(traceback.format_exc())
