#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
from bincrafters import build_shared


if __name__ == "__main__":
    with open("groups.json") as json_file:
        json_data = json.load(json_file)

        for packages in json_data.values():
            for package in packages:
                recipe = "conanfile-{}.py".format(package.lower())
                version = build_shared.get_version_from_recipe(recipe)
                subprocess.check_call(["conan", "export", recipe, "bincrafters/testing"])
