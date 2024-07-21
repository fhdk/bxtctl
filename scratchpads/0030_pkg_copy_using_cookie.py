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

import json
import time
import requests
from Bxt.BxtConfig import BxtConfig
from requests import Request, utils


"""
part three of four in a series of scratchpads
copies the test packages

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

from_section = {
    "branch": "testing",
    "repository": "extra",
    "architecture": "x86_64"
}
to_section = {
    "branch": "testing",
    "repository": "extra",
    "architecture": "aarch64"
}


dummy1 = "a-dummy1"
dummy2 = "a-dummy2"

form_content = json.dumps([
    {"name": dummy1, "from_section": from_section, "to_section": to_section},
    {"name": dummy2, "from_section": from_section, "to_section": to_section}])

form_data = {("to_copy", (None, form_content))}

headers = {
    "Accept": "application/json",
    "Content-Type": "multipart/form-data"
}

session = requests.Session()
session.cookies.update({"token": token})
request = Request('POST', endpoint, files=form_data, headers=headers)

req = request.prepare()

cookie_jar = requests.utils.dict_from_cookiejar(session.cookies)
print("bxt_copy_pkg   : CookieAuth")
print(f"cookiejar     : token = {cookie_jar["token"][:15]}...{cookie_jar["token"][-15:]}")
print(f"req headers   : {headers}")
print(f"req url       : {req.url}")
print(f"form data     : {req.body}")

print("request begin    --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
response = session.send(req, stream=True)

print("response recv    --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
print("response headers --> ", response.headers)
print("response status  --> ", response.status_code)
print("response content --> ", response.content)
