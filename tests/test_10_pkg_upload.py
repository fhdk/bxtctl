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
Part one of four in a series of tests
Commits a test package to stable -> multilib -> x86_64 repo

For now the result is verified by using the WebUI
A later update will use the packages list endpoint 
to verify the package exist at the target repo 
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

test_repo = os.path.join(os.path.dirname(__file__), "../repo")
test_pkg_1 = "arch-install-scripts-28-1-any.pkg.tar.zst"
test_pkg_2 = "abseil-cpp-20240116.2-2-x86_64.pkg.tar.zst"
upload_section = {
    "branch": "unstable",
    "repository": "multilib",
    "architecture": "x86_64"
}

bxt_upload_form = {
    ("package1.file", (test_pkg_1, open(f"{test_repo}/{test_pkg_1}", "rb"))),
    ("package1.signature", (f"{test_pkg_1}.sig", open(f"{test_repo}/{test_pkg_1}.sig", "rb"))),
    ("package1.section", (None, json.dumps(upload_section))),
    ("package2.file", (test_pkg_2, open(f"{test_repo}/{test_pkg_2}", "rb"))),
    ("package2.signature", (f"{test_pkg_2}.sig", open(f"{test_repo}/{test_pkg_2}.sig", "rb"))),
    ("package2.section", (None, json.dumps(upload_section))),
}

headers = {"Authorization": f"Bearer {token}"}

req = requests.session()
req.headers.update(headers)

print("bxt_upload_form : ")
pprint(bxt_upload_form)
print("upload request begin --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
response = req.post(endpoint, files=bxt_upload_form)
print("upload response recv --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
print("                 headers ", response.headers)
print("                 status  ", response.status_code)
