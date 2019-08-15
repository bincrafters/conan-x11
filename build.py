#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
import sys
import tempfile
from bincrafters import build_template_default, build_shared
from conans import tools

if __name__ == "__main__":
    subprocess.check_call([sys.executable, "manage.py", "gen"])
    subprocess.check_call([sys.executable, "manage.py", "groups"])

    with open("groups.json") as json_file:
        json_data = json.load(json_file)

    cache_folder = tempfile.mkdtemp("conan")
    docker_args = "'-v ${PWD}:/home/conan/.conan/data'"
    for packages in json_data.values():
        for package in packages:
            recipe = "conanfile-{}.py".format(package.lower())
            version = build_shared.get_version_from_recipe(recipe)
            with tools.environment_append({
                "CONAN_CONANFILE": recipe,
                "CONAN_VERSION": version,
                "CONAN_DOCKER_RUN_OPTIONS": docker_args
                }):
                builder = build_template_default.get_builder(docker_args)
                builder.run()
