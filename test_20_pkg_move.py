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
import json
import time

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

"""
part two of four in a series of tests
moves the test package
from: stable -> multilib -> x86_64 repo
to: stable -> extra -> x86_64 repo

For now the result is verified by using the WebUI
A later update will use the packages list endpoint 
to verify the package moved to the target repo 
"""

config = BxtConfig()

if not config.is_valid():
    y = config.configure()

if not config.get_access_token():
    z = config.login()


if config.is_token_expired():
    if not config.renew_access_token():
        z = config.login()

token = config.get_access_token()
endpoint = f"{config.get_url()}/{config.endpoint["pkgCommit"]}"

test_repo = os.path.join(os.path.dirname(__file__), "repo")
test_pkg = "arch-install-scripts-28-1-any.pkg.tar.zst"

section_a = {
    "branch": "stable",
    "repository": "multilib",
    "architecture": "x86_64"
}

section_b = {
    "branch": "stable",
    "repository": "extra",
    "architecture": "x86_64"
}

bxt_move_pkg = {
    ("to_move", json.dumps([{"name": test_pkg, "from_section": section_a, "to_section": section_b}])),
}

headers = {"Authorization": f"Bearer {token}"}

req = requests.session()
req.headers.update(headers)

print("bxt_move_pkg : ")
pprint(bxt_move_pkg)
print("move request begin --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
response = req.post(endpoint, files=bxt_move_pkg)
print("move response recv --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
print("               headers ", response.headers)
print("               status  ", response.status_code)
