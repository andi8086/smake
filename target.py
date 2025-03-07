import logging

class Target:
        def __init__(self, name, settings):
                print(settings)


def TargetFactory(name, settings):
        logger = logging.getLogger('TargetFactory')

        if not 'type' in settings:
                logger.error(f'Missing target type for target {name}')
                raise Exception('Target missing type')

        return Target(name, settings)
