#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
import sys
import shutil
from bincrafters import build_template_default
from conans import tools

if __name__ == "__main__":
    subprocess.check_call([sys.executable, "manage.py", "gen"])
    subprocess.check_call([sys.executable, "manage.py", "groups"])

    with open("groups.json") as json_file:
        json_data = json.load(json_file)

    for packages in json_data.values():
        for package in packages:
            shutil.move("conanfile-{}.py".format(package), "conanfile.py")
            builder = build_template_default.get_builder()
            builder.run()
