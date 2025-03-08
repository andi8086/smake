from schema import Schema, SchemaError
import yaml
import logging
from compiler import Compiler
import target
import os


CONFIG_VERSION = 1

config_schema = Schema({
        "version": int,
        "targets": [str],
        str: object or dict or list
})

class Config:
        logger = None
        targets = set()
        project_dir = ""
        config_file = ""
        build_dir = ""
        global_vars = {}

        def __init__(self, config, builddir):
                self.global_vars = {}
                self.logger = logging.getLogger("config")
                self.config_file = os.path.abspath(config)
                self.project_dir = os.path.dirname(self.config_file)
                self.logger.info(f"Project directory {self.project_dir}")
                if os.path.isabs(builddir):
                        self.build_dir = builddir
                else:
                        self.build_dir = os.path.join(
                                self.project_dir,
                                builddir)
                self.logger.info(f"Build directory {self.build_dir}")
                with open(config) as stream:
                        self.cfg = yaml.safe_load(stream)
                try:
                        config_schema.validate(self.cfg)
                        self.logger.info(
                                "Build configuration validated.")
                except SchemaError as se:
                        raise se

        def parse_include(self, include):
                icfg = None
                with open(include) as stream:
                        icfg = yaml.safe_load(stream)

                self.logger.info(f"Including {include}")
                if 'global' in icfg:
                        for key, val in icfg['global'].items():
                                self.global_vars[key] = val

        def parse(self):
                if self.cfg['version'] != CONFIG_VERSION:
                        self.logger.error(
                                "Invalid Config Version {}".format(
                                        self.cfg['version']))
                        raise Exception("Invalid Config Version")

                if "includes" in self.cfg:
                        includes = self.cfg['includes']

                        for i in includes:
                                # rel path is relative to project_dir
                                if os.path.isabs(i):
                                        if os.path.isfile(i):
                                                self.parse_include(i)
                                else:
                                        relpath = os.path.join(self.project_dir, os.path.dirname(i))
                                        i = os.path.join(relpath, os.path.basename(i))
                                        self.parse_include(i)

                for t in self.cfg['targets']:
                        # Check if target has a definition
                        if not t in self.cfg:
                                self.logger.error(
                                        "Missing target definition for {}".
                                      format(t))
                                raise Exception("Missing target definition")

                        tar = target.TargetFactory(t, self.cfg[t], self)

                        self.targets.add(tar)

                return True

