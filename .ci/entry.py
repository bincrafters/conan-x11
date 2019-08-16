#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess


if __name__ == "__main__":
    with open("groups.json") as json_file:
        json_data = json.load(json_file)
        for index in range(6):
            for package in json_data[str(index)]:
                recipe = "conanfile-{}.py".format(package.lower())
                subprocess.check_call(["conan", "export", recipe, "bincrafters/testing"])
