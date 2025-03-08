import os
from config import *

class build_tree:

        logger = None
        dryrun = False

        def __init__(self, logger, cfile = 'smake.yaml'):
                self.logger = logger
                self.dryrun = False
                try:
                        self.logger.info(f"Parsing {cfile}")
                        self.config = Config(cfile)
                        self.config.parse()
                except:
                        raise Exception("Config Exception")

        def check_targets(self, targets):
                for t in targets:
                        if not t in self.config.targets:
                                self.logger.error(f"Target {t} not found")
                                raise Exception("Invalid target")

        def build_target_tree(self, targets):
                # find the corresponding target object
                # for each target and call its build method
                for t in targets:
                        for ct in self.config.targets:
                                if t != ct:
                                        continue
                                self.logger.debug(f"Current Target {t}")
                                self.logger.debug(f"is already built: {ct.built}")
                                if not ct.built:
                                        self.logger.debug(f"Deps: {ct.deps()}")
                                        self.build_target_tree(ct.deps())
                                        self.logger.info(f"Building {ct.name}")
                                        ct.build(dryrun=self.dryrun)
                                break

        def build(self, targets):
                self.logger.info(f"Building targets {targets}")
                # TODO: check dep targets as well
                self.check_targets(targets)
                self.build_target_tree(targets)

        def clean_target_tree(self, targets):
                # find the corresponding target object
                # for each target and call its clean method
                for t in targets:
                        for ct in self.config.targets:
                                if t != ct:
                                        continue
                                self.logger.debug(f"Current Target {t}")
                                if not ct.cleaned:
                                        self.logger.debug(f"Deps: {ct.deps()}")
                                        self.clean_target_tree(ct.deps())
                                        self.logger.info(f"Cleaning {ct.name}")
                                        ct.clean(dryrun=self.dryrun)
                                break

        def clean(self, targets):
                self.logger.info(f"Cleaning targets {targets}")
                self.check_targets(targets)
                self.clean_target_tree(targets)
