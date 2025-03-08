import logging
import executor


class Target:
        name = None
        logger = None
        _deps = None
        built = False
        cleaned = False

        def __init__(self, name, settings):
                self.name = name
                self.settings = settings
                self._deps = set()
                self.cleaned = False
                self.built = False

        def getName(self):
                return self.name

        def deps(self):
                return self._deps

        def __hash__(self):
                return hash(self.name)

        def __eq__(self, other):
                if type(other) == str:
                        return self.name == other
                return self.name == other.name

        def build(self, dryrun):
                pass

        def clean(self, dryrun):
                pass


class TargetExe(Target):
        def __init__(self, name, settings):
                super().__init__(name, settings)
                self.logger = logging.getLogger('TargetExe')
                self.logger.debug(f'Creating target {name}')

        def build(self, dryrun):
                x = executor.Executor(dryrun)
                if not x.run("gcc -v"):
                        self.logger.error(f'Build error')
                self.built = True

        def clean(self, dryrun):
                self.cleaned = True


class TargetLib(Target):
        def __init__(self, name, settings):
                super().__init__(name, settings)
                self.logger = logging.getLogger('TargetLib')
                self.logger.debug(f'Creating target {name}')

        def build(self, dryrun):
                self.built = True

        def clean(self, dryrun):
                self.cleaned = True


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
                        self._deps.add(st)

        def build(self, dryrun):
                self.built = True

        def clean(self, dryrun):
                self.cleaned = True


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
