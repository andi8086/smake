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

        def __init__(self, config, builddir):
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

        def parse(self):
                if self.cfg['version'] != CONFIG_VERSION:
                        self.logger.error(
                                "Invalid Config Version {}".format(
                                        self.cfg['version']))
                        raise Exception("Invalid Config Version")

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

