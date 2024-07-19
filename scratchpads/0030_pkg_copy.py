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
from requests import Session
from requests import Request


"""
part three of four in a series of scratchpads
copies the test package
from: stable -> extra -> x86_64 repo
to: stable -> multilib -> x86_64 repo

For now the result is verified by using the WebUI
A later update will use the packages list endpoint 
to verify the package now exist at both targets
"""

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

test_pkg = "arch-install-scripts"

from_section = {"branch": "unstable", "repository": "multilib", "architecture": "x86_64"}
to_section = {"branch": "testing", "repository": "extra", "architecture": "x86_64"}
pkg_name = "arch-install-scripts"

form_content = json.dumps([{"name": pkg_name, "from_section": from_section, "to_section": to_section}])
form_data = {("to_copy", (None, form_content))}

headers = {"Authorization": f"Bearer {token}", "Accept": "application/json", "Content-Type": "multipart/form-data"}

session = requests.Session()
request = Request('POST', endpoint, files=form_data, headers=headers)
req = request.prepare()

print("bxt_copy_pkg : ")
print(f"req headers : {req.headers}")
print(f"req url     : {req.url}")
print(f"form data   : {req.body}: ")

print("copy request begin --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
response = session.send(req)

print("response recv --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
print("      headers --> ", response.headers)
print("       status --> ", response.status_code)