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
from Bxt.BxtSession import BxtSession
import jwt
from pprint import pprint
import os

config = BxtConfig()

if not config.valid_config():
    y = config.configure()

if not config.get_access_token():
    z = config.login()

if config.valid_token():
    if not config.renew_access_token():
        z = config.login()

token = config.get_access_token()
endpoint = f"{config.get_url()}/{config.endpoint["pkgCommit"]}"

test_repo = os.path.join(os.path.dirname(__file__), "repo")
test_pkg = "arch-install-scripts-28-1-any.pkg.tar.zst"
upload_target = {"branch": "stable", "repository": "multilib", "architecture": "x86_64"}
upload_form = {
    ("package1.file", (test_pkg, open(f"{test_repo}/{test_pkg}", "rb"))),
    (
        "package1.signatureFile",
        (f"{test_pkg}.sig", open(f"{test_repo}/{test_pkg}.sig", "rb")),
    ),
    ("package1.section", (None, json.dumps(upload_target))),
}

headers = {"Authorization": f"Bearer {token}"}

print("upload_form : ")
print(upload_form)
req = requests.session()
req.headers.update(headers)

print("request begin --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
response = req.post(endpoint, files=upload_form)
print("response recv --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
print("          headers ", response.headers)
print("          status  ", response.status_code)
