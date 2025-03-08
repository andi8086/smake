import subprocess
import os
import sys
import pathlib
import logging


class Executor:
        logger = None
        env = None
        dryrun = False

        def __init__(self, dryrun):
                self.logger = logging.getLogger('Exec')
                # self.env = os.environ.copy()
                self.env = {}
                self.dryrun = dryrun

        def run(self, cmd):
                if self.dryrun:
                        self.logger.info(f"Dryrun: Command: {cmd}")
                        return True

                p = subprocess.Popen(cmd, shell=True,
                        env=self.env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
                for line in p.stdout.readlines():
                        self.logger.info(line.decode("UTF-8"))
                retval = p.wait()
                self.logger.info(f"Return value {retval}")

                return retval == 0
