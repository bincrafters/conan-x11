#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
import sys
from bincrafters import build_template_default, build_shared
from conans import tools

if __name__ == "__main__":
    subprocess.check_call([sys.executable, "manage.py", "gen"])
    subprocess.check_call([sys.executable, "manage.py", "groups"])

    with open("groups.json") as json_file:
        json_data = json.load(json_file)

    for packages in json_data.values():
        for package in packages:
            recipe = "conanfile-{}.py".format(package)
            version = build_shared.get_version_from_recipe(recipe)
            with tools.environment_append({
                "CONAN_CONANFILE": recipe,
                "CONAN_VERSION": version
                }):
                builder = build_template_default.get_builder()
                builder.run()
