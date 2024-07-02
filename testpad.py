#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# bxtctl is command line client designed to interact with bxt api
# bxt can be found at https://gitlab.com/anydistro/bxt
#
# bxtctl is free software: you can redistribute it and/or modify
# it under the terms of the Affero GNU General Public License
# as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# bxtctl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the Affero GNU General Public License
# along with bxtctl.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors: Frede Hundewadt https://github.com/fhdk/bxtctl
#

import argparse
import cmd2
import requests
from cmd2 import Cmd2ArgumentParser, with_argparser
import sys
from Bxt.BxtAcl import BxtAcl
from Bxt.BxtConfig import BxtConfig
from Bxt.Http import Http
import jwt
from pprint import pprint
import os

# config = BxtConfig()
#
# if not config.is_valid():
#     y = config.configure()
#
# if not config.get_access_token():
#     z = config.login()
#
# # prompt = f"({config.get_name()}@bxt) $ "
# http = Http(BxtConfig.user_agent)
# http.set_access_token(config.get_access_token())
# sections = http.get_sections(f"{config.get_url()}/{BxtConfig.endpoint['sections']}")
# print(f"sections: {sections}\n")

test_repo = os.path.join(os.path.dirname(__file__), "repo")
files = {
    ("packageFile", (None, f"{test_repo}/abseil-cpp-20240116.2-2-x86_64.pkg.tar.zst")),
    (
        "packageSignature",
        (None, f"{test_repo}/abseil-cpp-20240116.2-2-x86_64.pkg.tar.zst.sig"),
    ),
    ("packageFile", (None, f"{test_repo}/arch-install-scripts-28-1-any.pkg.tar.zst")),
    (
        "packageSignature",
        (None, f"{test_repo}/arch-install-scripts-28-1-any.pkg.tar.zstsig"),
    ),
}
body = {
    "packageSection": {
        "branch": "unstable",
        "repository": "extra",
        "architecture": "x86_64",
    }
}
response = requests.request("post", "https://httpbin.org/post", files=files, json=body)
print("  --> response headers")
pprint(response.json()["headers"])
print("  --> response json")
pprint(response.json())
