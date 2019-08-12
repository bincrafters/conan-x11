#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import print_function
import argparse
import sys
import subprocess
import json

conanfile_template = """from conans import tools
import os
from conanfile_base import {baseclass}

class {classname}Conan({baseclass}):
    basename = "{name}"
    name = basename.lower()
    version = "{version}"
    tags = ("conan", "{name}")
    description = '{description}'
    exports = ["conanfile_base.py"]

    {requires}

    def source(self):
        url = "https://www.x.org/archive/individual/{namespace}/{name}-{version}.tar.gz"
        tools.get(url, sha256="{sha256}")
        extracted_dir = "{name}-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package_info(self):
        super({classname}Conan, self).package_info()
        {libs}
"""

libraries = json.load(open("x11.json"))


def find(name):
    for info in libraries:
        if info["name"] == name:
            return info
    raise Exception("not found %s" % name)


def gen(args):
    for info in libraries:
        name = info["name"]
        filename = "conanfile-%s.py" % name.lower()
        print("generating %s..." % filename)
        classname = name.replace("-", "")
        with open(filename, "w") as f:
            if "requires" in info:
                requires = []
                for require in info["requires"]:
                    if "@" in require:
                        requires.append('"%s"' % require)
                    else:
                        requires.append('"%s/%s@bincrafters/testing"' % (require.lower(), find(require)["version"]))
                requires = ", ".join(requires)
                requires = "requires = (" + requires + ")"
            else:
                requires = ""
            header_only = "header-only" in info and info["header-only"]
            libs = ""
            if "libs" in info:
                libs = ['"%s"' % lib for lib in info["libs"]]
                libs = "self.cpp_info.libs.extend([%s])" % ", ".join(libs)
            elif not header_only:
                libs = ['"%s"' % name[3:]]
                libs = "self.cpp_info.libs.extend([%s])" % ", ".join(libs)
            baseclass = "BaseHeaderOnly" if header_only else "BaseLib"
            namespace = info["namespace"] if "namespace" in info else "lib"
            content = conanfile_template.format(sha256=info["sha256"],
                                                version=info["version"],
                                                description=info["description"],
                                                namespace=namespace,
                                                requires=requires,
                                                name=name,
                                                baseclass=baseclass,
                                                libs=libs,
                                                classname=classname)
            f.write(content)


def create(args):
    for info in libraries:
        name = info["name"]
        filename = "conanfile-%s.py" % name.lower()
        subprocess.check_call(["conan", "create", filename, "bincrafters/testing", "-k"])
    #"--build", "missing"])


def groups(args):
    def in_groups(require, groups):
        for group in groups:
            if require in group:
                return True
        return False

    def all_requires_in_groups(requires, groups):
        for require in requires:
            if "@" not in require:
                if not in_groups(require, groups):
                    return False
        return True

    remain = libraries
    groups = []
    while remain:
        current_group = []
        for info in remain:
            requires = info["requires"] if "requires" in info else []
            if all_requires_in_groups(requires, groups):
                current_group.append(info["name"])
        groups.append(current_group)
        remain = [r for r in remain if r["name"] not in current_group]
    index = 0
    for group in groups:
        print("group %s: %s" % (index, group))
        index = index + 1


def main(args):
    parser = argparse.ArgumentParser(description='utility script to manage conan X11 package')
    subparsers = parser.add_subparsers()
    sp_gen = subparsers.add_parser('gen', help='generate conanfiles')
    sp_create = subparsers.add_parser('create', help='invoke conan create on conanfiles')
    sp_groups = subparsers.add_parser('groups', help='report groups')
    sp_gen.set_defaults(func=gen)
    sp_create.set_defaults(func=create)
    sp_groups.set_defaults(func=groups)
    args = parser.parse_args(args)
    args.func(args)


if __name__ == '__main__':
    main(sys.argv[1:])
