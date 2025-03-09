import os
from config import *
from target import all_targets
import re

class build_tree:

        logger = None
        dryrun = False
        builddir = ""

        def __init__(self, logger, builddir, cfile = 'smake.yaml'):
                self.logger = logger
                self.dryrun = False
                try:
                        self.logger.info(f"Parsing {cfile}")
                        self.config = Config(cfile, builddir)
                        self.config.parse()
                        self.builddir = self.config.build_dir
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
                        t_builddir = all_targets[t].get_build_dir(self.builddir)
                        t_builddir = os.path.abspath(t_builddir)
                        print(f"{t}: {t_builddir}")
                        for ct in self.config.targets:
                                if t != ct:
                                        continue
                                self.logger.debug(f"Current Target {t}")
                                self.logger.debug(f"is already built: {ct.built}")
                                if not ct.built:
                                        self.logger.debug(f"Deps: {ct.deps()}")
                                        self.build_target_tree(ct.deps())
                                        self.logger.info(f"Building {ct.name}")
                                        ct.build(self.dryrun, self.config.build_dir)
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
                                        ct.clean(self.dryrun, self.config.build_dir)
                                break

        def clean(self, targets):
                self.logger.info(f"Cleaning targets {targets}")
                self.check_targets(targets)
                self.clean_target_tree(targets)

        def subst_BS(self, v):
                tname = re.findall('\\$B\\(([A-Za-z0-9_]+)\\)', v)
                if len(tname) > 0:
                        for n in tname:
                                v = v.replace(f'$B({n})',
                                        str(all_targets[n].get_build_dir(self.builddir)))
                tname = re.findall('\\$S\\(([A-Za-z0-9_]+)\\)', v)
                if len(tname) > 0:
                        for n in tname:
                                v = v.replace(f'$S({n})', all_targets[n].source_dir)
                return v

        def var_subst(self):
                for t in all_targets:
                        # Check if we have variables
                        variables = []
                        if 'vars' in all_targets[t].settings:
                                variables = all_targets[t].settings['vars']
                        for k in variables:
                                values = variables[k]
                                if not type(values) == list:
                                        values = self.subst_BS(values)
                                else:
                                        values = [self.subst_BS(v) for v in values]
                                variables[k] = values
                        all_targets[t].settings['vars'] = variables
                        print(variables)
