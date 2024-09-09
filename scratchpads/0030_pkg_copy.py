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
from src.Bxt.BxtConfig import BxtConfig
from requests import Request
from requests import RequestException
import uuid

"""
part three of four in a series of scratchpads
copies the test package

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

from_section = {"branch": "testing", "repository": "extra", "architecture": "x86_64"}
to_section = {"branch": "testing", "repository": "extra", "architecture": "aarch64"}

form_content = json.dumps(
    [
        {"name": "a-dummy1", "from_section": from_section, "to_section": to_section},
        {"name": "a-dummy2", "from_section": from_section, "to_section": to_section},
        {"name": "a-dummy3", "from_section": from_section, "to_section": to_section},
    ]
)

files = {("to_copy", (None, form_content, "application/json"))}

headers = {
    "User-Agent": config.user_agent,
    "Authorization": f"Bearer {token}",
    "X-BxtCtl-Request-Id": str(uuid.uuid4()),
}

session = requests.Session()
request = Request("POST", endpoint, headers=headers, files=files)

req = request.prepare()

print("bxt_copy_pkg  : BearerAuth")
to_be_printed = req.headers.copy()
to_be_printed["Authorization"] = f"Bearer {token[:15]}...{token[-15:]}"
print(f"req headers   : {to_be_printed}")
print(f"req url       : {req.url}")
print(f"req body      : {req.body}")
print("--------------------------------------------------------------")
print("request begin    --> ", time.strftime("%Y-%m-%d %H:%M:%S"))

try:

    response = session.send(req, timeout=30)

except RequestException as e:
    print("RequestException --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
    print(e)
    exit(1)

print("response recv    --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
print("response headers --> ", response.headers)
print("response status  --> ", response.status_code)
print("response content --> ", response.content)
