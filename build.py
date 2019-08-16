#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
import sys
import os
from bincrafters import build_template_default, build_shared
from conans import tools
from conans.client import conan_api

if __name__ == "__main__":
    subprocess.check_call([sys.executable, "manage.py", "gen"])
    subprocess.check_call([sys.executable, "manage.py", "groups"])

    with open("groups.json") as json_file:
        json_data = json.load(json_file)

    cache_dir = "data"
    tools.rmdir(cache_dir)
    tools.mkdir(cache_dir)
    path = os.path.abspath(cache_dir)
    docker_args = "-v {}:/home/conan/.conan/data".format(path)
    entry_script = ".ci/entry.py"
    conan_instance, _, _ = conan_api.Conan.factory()

    for package in json_data["6"]:
        recipe = "conanfile-{}.py".format(package.lower())
        test_package_folder = "test_package-{}".format(package.lower())
        version = conan_instance.inspect(path=recipe, attributes=["version"])["version"]
        print(f"VERSIONS: {version}")
        print(f"RECIPE: {recipe}")
        with tools.environment_append({
            "CONAN_CONANFILE": recipe,
            "CONAN_VERSION": version,
            # "CPT_TEST_FOLDER": test_package_folder
            "CONAN_DOCKER_RUN_OPTIONS": docker_args
            }):
            builder = build_template_default.get_builder(docker_args, docker_entry_script=entry_script)
            builder.update_build_if(lambda build: True, new_env_vars={"MAKEFLAGS": "--silent"})
            builder.run()
