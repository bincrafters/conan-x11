#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
import sys
from bincrafters import build_template_default
from conans import tools

if __name__ == "__main__":
    subprocess.check_call([sys.executable, "manage.py", "gen"])
    subprocess.check_call([sys.executable, "manage.py", "groups"])

    with open("groups.json") as json_file:
        json_data = json.load(json_file)

    for packages in json_data.values():
        print(packages)
        for package in packages:
            with tools.environment_append({"CONAN_CONANFILE": "conanfile-{}.py".format(package)}):
                builder = build_template_default.get_builder()
                builder.run()
