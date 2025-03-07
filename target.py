import logging

class Target:
        name = None
        logger = None
        def __init__(self, name, settings):
                self.name = name
                self.settings = settings

        def getName(self):
                return self.name

        def __hash__(self):
                return hash(self.name)

        def __eq__(self, other):
                return self.name == other.name


class TargetExe(Target):
        def __init__(self, name, settings):
                super().__init__(name, settings)
                self.logger = logging.getLogger('TargetExe')
                self.logger.debug(f'Creating target {name}')


class TargetLib(Target):
        def __init__(self, name, settings):
                super().__init__(name, settings)
                self.logger = logging.getLogger('TargetLib')
                self.logger.debug(f'Creating target {name}')

class TargetAlias(Target):
        def __init__(self, name, settings):
                super().__init__(name, settings)
                self.logger = logging.getLogger('TargetAlias')
                self.logger.debug(f'Creating target {name}')
                if not 'targets' in settings:
                        self.logger.error('Missing targets in alias target')
                        raise Exception('Missing targets in alias target')
                for st in settings['targets']:
                        self.logger.debug(f'Adding subtarget {st}')

def TargetFactory(name, settings):
        logger = logging.getLogger('TargetFactory')

        if not 'type' in settings:
                logger.error(f'Missing type for target {name}')
                raise Exception('Target missing type')

        if settings['type'] in ['x', 'exe', 'executable']:
                return TargetExe(name, settings)

        if settings['type'] in ['l', 'lib', 'library']:
                return TargetLib(name, settings)

        if settings['type'] in ['a', 'alias']:
                return TargetAlias(name, settings)

        return Target(name, settings)
