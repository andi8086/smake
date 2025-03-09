import logging
import executor
import re
import os
from pathlib import Path
import shutil


# After all targets have been created, this
# is a list of references to all the targets, so that
# every target can access properties of all other targets
# Keep it simple and stupid here
all_targets = dict()


class Target:
        name = None
        logger = None
        _deps = None
        built = False
        cleaned = False
        tvars = {}
        script = []
        compile_cmds = {}
        objects = []
        source_dir = ""
        link_cmd = None

        def __init__(self, name, settings):
                self.name = name
                self.settings = settings
                self._deps = set()
                self.cleaned = False
                self.built = False
                self.tvars = {}
                self.script = []
                self.compile_cmds = {}
                self.objects = []
                self.link_cmd = None

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

        def build(self, dryrun, builddir):
                pass

        def clean(self, dryrun, builddir):
                pass

        def var_subst(self, cmd):
                cmd_vars = re.findall("\\$[a-zA-Z0-9_]*", cmd)
                # Replace one by one with descending length
                sorted_vars = sorted(cmd_vars, key=len)
                sorted_vars.reverse()
                for v in sorted_vars:
                        key = v[1:]
                        if key in self.tvars:
                                val = self.tvars[key]
                                if type(val) == list:
                                        val = (' ').join(val)
                                cmd = cmd.replace(v, val)
                return cmd

        def get_build_dir(self, builddir):
                # Appends build_prefix and returns the full path
                opath = Path(os.path.join(builddir, self.build_prefix))
                return opath

        def push_build_dir(self, builddir):
                self.old_cwd = os.getcwd()

                # Check if build_dir/build_prefix exists
                opath = self.get_build_dir(builddir)
                opath.mkdir(parents=True, exist_ok=True)

                self.logger.info(f"Entering directory {opath}")
                os.chdir(opath)

        def path_restore(self):
                self.logger.info(f"Leaving directory {os.getcwd()}")
                os.chdir(self.old_cwd)


class TargetConfig(Target):
        def __init__(self, name, settings):
                super().__init__(name, settings)
                self.logger = logging.getLogger('TargetConfig')
                self.logger.debug(f'Creating target {name}')
                if not 'source' in settings:
                        raise Exception("Missing source in config target")
                self.input = settings['source']

        def build(self, dryrun, builddir):
                self.logger.debug(f'vars = {self.tvars}')
                self.built = True

                self.input = os.path.join(self.source_dir, self.input)
                self.logger.info(f'Config template is {self.input}')

                self.push_build_dir(builddir)
                outname = Path(os.path.basename(self.input)).stem

                outname = os.path.join(os.getcwd(), outname)

                shutil.copyfile(self.input, outname)
                # now open the file and replace variables

                self.logger.info(f'Generating {outname}')
                with open(outname, 'r+') as f:
                        file = f.read()

                        cvars = re.findall('\\@([a-zA-Z0-9_]+)\\@', file)
                        cvars = sorted(cvars, key=len)
                        cvars.reverse()
                        cvars = list(set(cvars))

                        for v in cvars:
                                if v in self.global_vars:
                                        file = file.replace(f"@{v}@",
                                                self.global_vars[v])

                        f.seek(0)
                        f.write(file)
                        f.truncate()

                self.path_restore()


class TargetExe(Target):
        def __init__(self, name, settings):
                super().__init__(name, settings)
                self.logger = logging.getLogger('TargetExe')
                self.logger.debug(f'Creating target {name}')

        def build(self, dryrun, builddir):
                self.logger.debug(f'vars = {self.tvars}')

                self.push_build_dir(builddir)
                x = executor.Executor(dryrun)

                for o in self.objects:
                        # check that path is not absolute
                        if os.path.isabs(o):
                                self.path_restore()
                                raise Exception("object path must be relative")

                        obj_file = os.path.join(self.build_prefix, o)

                        # Get basename of object file
                        basename = Path(o).stem
                        dirname = os.path.dirname(o)

                        # check all registered exts from compile_each rules
                        # to look for a matching source file
                        src_file = None
                        command_list = []

                        for e in self.compile_cmds:
                                testfile = os.path.join(self.source_dir,
                                        dirname, basename + '.' + e)
                                self.logger.debug(f'testing src {testfile}')
                                if os.path.isfile(testfile):
                                        src_file = testfile
                                        command_list = self.compile_cmds[e]
                                        break
                        if not src_file:
                                self.path_restore()
                                raise Exception(f"Missing source for {o}")

                        # We found a source file, compile it
                        self.logger.debug(f'compile {src_file} to {o}')
                        self.logger.info(f'[COMPILE] {obj_file}')
                        self.logger.debug(f'command list: {command_list}')

                        # Check if directory for o exists
                        if not os.path.exists(os.path.dirname(o)):
                                Path(os.path.dirname(o)).mkdir(parents=True, exist_ok=True)

                        for cmd in command_list:
                                cmd = cmd.replace("$input", '"' + src_file + '"')
                                cmd = cmd.replace("$output", '"' + o + '"')
                                # Substitute target variables
                                cmd = self.var_subst(cmd)
                                x.run(cmd)

                if self.link_cmd:
                        if type(self.link_cmd) != list:
                                self.link_cmd = [self.link_cmd]
                        for cmd in self.link_cmd:
                                cmd = cmd.replace("$objects", ' '.join(self.objects))
                                cmd = self.var_subst(cmd)
                                x.run(cmd)

                self.path_restore()
                self.built = True

        def clean(self, dryrun, builddir):
                self.cleaned = True


class TargetLib(Target):
        def __init__(self, name, settings):
                super().__init__(name, settings)
                self.logger = logging.getLogger('TargetLib')
                self.logger.debug(f'Creating target {name}')

        def build(self, dryrun, builddir):
                self.built = True

        def clean(self, dryrun, builddir):
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

        def build(self, dryrun, builddir):
                self.built = True

        def clean(self, dryrun, builddir):
                self.cleaned = True


def TargetFactory(name, settings, config_obj):
        logger = logging.getLogger('TargetFactory')
        new_target = None

        if not 'type' in settings:
                logger.error(f'Missing type for target {name}')
                raise Exception('Target missing type')

        if settings['type'] in ['x', 'exe', 'executable']:
                new_target = TargetExe(name, settings)
        elif settings['type'] in ['l', 'lib', 'library']:
                new_target = TargetLib(name, settings)
        elif settings['type'] in ['a', 'alias']:
                new_target = TargetAlias(name, settings)
        elif settings['type'] in ['c', 'config']:
                new_target = TargetConfig(name, settings)

        if 'depends' in settings:
                for d in settings['depends']:
                        # Check if target we depend on exists
                        if not d in config_obj.cfg:
                                raise Exception(f'Missing target definition for {d}')
                        new_target._deps.add(d)

        if 'vars' in settings:
                new_target.tvars = settings['vars']

        for key in settings:
                if re.match(r"compile_each_.+", key):
                        extension = key[len("compile_each_"):]
                        compile_cmds = {extension : settings[key]}
                        new_target.compile_cmds = compile_cmds

        if 'objects' in settings:
                new_target.objects = settings['objects']

        source_dir = '.'
        if 'source_dir' in settings:
                source_dir = settings['source_dir']

        new_target.source_dir = os.path.join(config_obj.project_dir, source_dir)
        logger.debug(f'souce dir = {new_target.source_dir}')

        if 'build_prefix' in settings:
                if os.path.isabs(settings['build_prefix']):
                        raise Exception(f'target build_prefix must be relative')
                new_target.build_prefix = settings['build_prefix']
        else:
                new_target.build_prefix = None

        if "link_all" in settings:
                new_target.link_cmd = settings["link_all"]


        new_target.global_vars = config_obj.global_vars

        all_targets[name] = new_target

        return new_target
