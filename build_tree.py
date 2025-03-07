import os
from config import *

class build_tree:

        logger = None

        def __init__(self, logger, cfile = 'smake.yaml'):
                self.logger = logger
                try:
                        self.logger.info(f"Parsing {cfile}")
                        self.config = Config(cfile)
                        self.config.parse()
                except:
                        raise Exception("Config Exception")


        def build(self, target = 'default'):
                self.logger.info(f"Building target {target}")
