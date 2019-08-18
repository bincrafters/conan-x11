#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
import sys
import os
from bincrafters import build_template_default, build_shared
from conans import tools
from conans.client import conan_api


def get_channel_name():
    if os.getenv("TRAVIS") and \
       os.getenv("TRAVIS_BRANCH") == "master" and \
       os.getenv("TRAVIS_PULL_REQUEST", "false") == "false":
       return "stable"
    return os.getenv("CONAN_CHANNEL", "testing")

def get_username():
    return os.getenv("CONAN_USERNAME", "bincrafters")

def export_recipes():
    channel = get_channel_name()
    namespace = "{}/{}".format(get_username(), get_channel_name())
    with open("groups.json") as json_file:
        json_data = json.load(json_file)
        for index in range(6):
            for package in json_data[str(index)]:
                recipe = "conanfile-{}.py".format(package.lower())
                subprocess.check_call(["conan", "export", recipe, namespace])


if __name__ == "__main__":
    subprocess.check_call([sys.executable, "manage.py", "gen"])
    subprocess.check_call([sys.executable, "manage.py", "groups"])

    with open("groups.json") as json_file:
        json_data = json.load(json_file)

    conan_instance, _, _ = conan_api.Conan.factory()
    env_vars = {}
    entry_script = None

    if tools.os_info.is_linux:
        cache_dir = "data"
        tools.rmdir(cache_dir)
        tools.mkdir(cache_dir)
        path = os.path.abspath(cache_dir)
        docker_args = "-v {}:/home/conan/.conan/data".format(path)
        entry_script = ".ci/entry.py"
        env_vars["CONAN_DOCKER_RUN_OPTIONS"] = docker_args
    elif tools.os_info.is_macos:
        export_recipes()

    for package in json_data["6"]:
        recipe = "conanfile-{}.py".format(package.lower())
        test_package_folder = "test_package-{}".format(package.lower())
        env_vars["CONAN_VERSION"] = conan_instance.inspect(path=recipe, attributes=["version"])["version"]
        env_vars["CONAN_CONANFILE"] = recipe
        with tools.environment_append(env_vars):
            builder = build_template_default.get_builder(docker_entry_script=entry_script)
            builder.update_build_if(lambda build: True, new_env_vars={"MAKEFLAGS": "--silent"})
            builder.run()
