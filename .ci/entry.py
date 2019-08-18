#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
import os


def get_channel_name():
    return os.getenv("CONAN_CHANNEL", "testing")


def get_username():
    return os.getenv("CONAN_USERNAME", "bincrafters")


if __name__ == "__main__":
    channel = get_channel_name()
    namespace = "{}/{}".format(get_username(), get_channel_name())
    with open("groups.json") as json_file:
        json_data = json.load(json_file)
        for index in range(6):
            for package in json_data[str(index)]:
                recipe = "conanfile-{}.py".format(package.lower())
                subprocess.check_call(["conan", "export", recipe, namespace])
