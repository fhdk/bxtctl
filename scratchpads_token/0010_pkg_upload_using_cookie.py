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

import time
import json
import requests
from Bxt.BxtConfig import BxtConfig
from requests import Request, utils

"""
Part one of four in a series of scratchpads
Commits a test package to stable -> multilib -> x86_64 repo

For now the result is verified by using the WebUI
A later update will use the packages list endpoint 
to verify the package exist at the target repo 
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

test_repo = config.workspace
test_pkg_1 = "a-dummy1-0-0-any.pkg.tar.zst"
test_pkg_2 = "a-dummy2-0-0-any.pkg.tar.zst"

to_section = {
    "branch": "testing",
    "repository": "extra",
    "architecture": "x86_64",
}

# formdata can be either a tuple or a dictionary
# tuple preserves the order the elements
# dictionary posts the data in arbitrary order
form_data = (
    ("package1.file", (test_pkg_1, open(f"{test_repo}/{test_pkg_1}", "rb"))),
    ("package1.signature",
     (f"{test_pkg_1}.sig", open(f"{test_repo}/{test_pkg_1}.sig", "rb"))),
    ("package1.section", (None, json.dumps(to_section))),
    ("package2.file", (test_pkg_2, open(f"{test_repo}/{test_pkg_2}", "rb"))),
    ("package2.signature",
     (f"{test_pkg_2}.sig", open(f"{test_repo}/{test_pkg_2}.sig", "rb"))),
    ("package2.section", (None, json.dumps(to_section))),
)

headers = {
    "Accept": "application/json",
    "Content-Type": "multipart/form-data"
}

# reminder on token handling
# basic token handling
# cookie_jar = request.utils.dict_from_cookiejar(session.cookies)
# token = cookie_jar["token"]
# session.cookies.update({"token": self._token})

session = requests.Session()
# add token with name 'token'
session.cookies.update({"token": token})
# add token with name 'access_token'
session.cookies.update({"access_token": token})
request = Request('POST', endpoint, files=form_data, headers=headers)

req = request.prepare()

cookie_jar = requests.utils.dict_from_cookiejar(session.cookies)
print("bxt_upload_pkg : CookieAuth")
print(f"cookiejar     : token: {cookie_jar["token"][:15]}...{cookie_jar["token"][-15:]}")
print(f"cookiejar     : access_token: {cookie_jar["access_token"][:15]}...{cookie_jar["access_token"][-15:]}")
print(f"req headers   : {headers}")
print(f"req url       : {req.url}")
print(f"form data     : {req.body}")

print("request begin    --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
response = session.send(req, stream=True)

print("response recv    --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
print("response headers --> ", response.headers)
print("response status  --> ", response.status_code)
print("response content --> ", response.content)
