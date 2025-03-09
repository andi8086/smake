smake - Simple Make - Suitable for real use cases

* GNU Make:
        Is old and hard to read/write. Environment variables and/or
        PATH modifications are cumbersome and often need additional scripts.
        Simple file operations like mkdir, rmdir, rm -rf, ... need
        cumbersome adaptation between different operating systems.
        There is no functionality for variable substitution in templates
        without using tools like 'envsubst' or 'm4'.
* CMake:
        Is over-engineered and mostly suitable for portable applications,
        not for embedded scenarios. It is great for CPP and packages which
        where written especially for CMake. Syntax is hokus pokus.
* meson:
        Doesn't support simple scenarios like force build or partial clean
        It is very stuborn regarding its rules and imposes a fixed
        directory structure upon its projects, which doesn't make sense
        for existing embedded projects.
        It also doesn't suport post-processing and pre-processing steps.
        Custom targets must be implemented via scripts.
* bitbake:
        One layer too high, it handles project dependencies, not
        Makefiles.

Often hardware SDKs come with their own embedded tooling which
doesn't make it easier. Often these tools use npm or even java.
This means there is a real need for easy custom rule integration!

Most build tools run into the scenario where multiple tools must be combined
including things like: make => bash => msys => sh => ... which makes it really
cumbersome to develope.

# Config files

`smake` is written in `python` and has Makefiles based on `yaml`.
It suports:

* Global variables
* Include files for global variables
* Target specific variables with magic macros and variable substitution
* Config template header creation for C similar to autotools
* Source and Build directory macros similar to bitbake recipes ($B and $S)
* Recursive and non-recursive clean (with and without dependencies)

See `smake.yaml` for an example.

This project has just started and is far from being complete for my own
use cases.
