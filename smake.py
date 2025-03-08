import sys
import traceback
import argparse
import logging
import yaml
from build_tree import *

LOGMIN = 0
LOGMAX = 4

class LogAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
                if not LOGMIN <= values <= LOGMAX:
                        raise argparse.ArgumentError(self,
                                f"log level must be between {LOGMIN} and {LOGMAX}")
                setattr(namespace, self.dest, values)


if __name__ != '__main__':
        sys.exit(-1)

PROGNAME = 'smake'
VERSION = '0.1'
DESCRIPTION = 'Super Make - v{} - ' \
        'A build tool with focus on embedded projects' \
        .format(VERSION)

EPILOG = 'Because everything sucks.'


# Main parser with global options
parser = argparse.ArgumentParser(
        prog = PROGNAME,
        description = DESCRIPTION,
        epilog = EPILOG)
parser.add_argument('-f', '--file', type=str, default='smake.yaml',
                    dest='makefile')
parser.add_argument('-L', '--loglevel', type=int, default=3,
                    dest='loglevel', action=LogAction)
parser.add_argument('-d', '--dryrun', action='store_true',
                    default=False, dest='dryrun')
parser.add_argument('-b', '--builddir', type=str,
                    dest='builddir', default='build')

subparsers = parser.add_subparsers(dest='subcommand')

# Common arguments for sub commands
common_parser = argparse.ArgumentParser(description='targets')
common_parser.add_argument('targets', default='default', nargs='*')

# sub commands
build_parser = subparsers.add_parser('build', parents=[common_parser],
                                     add_help=False)

clean_parser = subparsers.add_parser('clean', parents=[common_parser],
                                     add_help=False)

args = parser.parse_args()

logLevels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]


logger = logging.getLogger(PROGNAME)
logging.basicConfig(level = logLevels[args.loglevel],
     format='%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s',
     datefmt='%Y-%m-%d %H:%M:%S')

logging.addLevelName(logging.WARNING,
        "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName(logging.ERROR,
        "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))

if not args.subcommand in ['build', 'clean']:
        logger.error('Expecting command')
        parser.print_help()
        sys.exit(1)

try:
        tree = build_tree(logger, args.builddir, cfile=args.makefile)
        tree.dryrun = args.dryrun
        func = getattr(tree, args.subcommand)
        func(args.targets)

except Exception as err:
        logger.exception(traceback.format_exc())
