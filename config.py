from schema import Schema, SchemaError
import yaml
import logging
from compiler import Compiler
import target


CONFIG_VERSION = 1

config_schema = Schema({
        "version": int,
        "targets": [str],
        str: object or dict or list
})

class Config:
        logger = None

        def __init__(self, config):
                self.logger = logging.getLogger("config")
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
                        print(t)
                        tar = target.TargetFactory(t, self.cfg[t])

                return True

