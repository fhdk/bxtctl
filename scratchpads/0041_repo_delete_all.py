# -*- coding: utf-8 -*-
#
# bxtctl is a command line client designed to interact
# with bxt api which can be found at https://gitlab.com/anydistro/bxt
#
# BxtCtl is free software: you can redistribute it and/or modify
# it under the terms of the Affero GNU General Public License
# as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# BxtCtl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the Affero GNU General Public License
# along with bxtctl.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors: Frede Hundewadt https://github.com/fhdk/bxtctl
#

import json
import time
import uuid

import requests
from bxtctl.Bxt.BxtConfig import BxtConfig
from bxtctl.Bxt.BxtSession import BxtSession
from requests import Request
from requests import RequestException

"""
part four of four in a series of scratchpads
deletes the test package

For now the result is verified by using the WebUI
A later update will use the packages list endpoint 
to verify the package is removed form both targets
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
endpoint_rm = f"{config.get_url()}/{config.endpoint["pkgCommit"]}"
from_section = {"branch": "testing", "repository": "extra", "architecture": "x86_64"}

endpoint_list = f"{config.get_url()}/{config.endpoint["pkgList"]}"
http = BxtSession(config.user_agent)

pkgs = http.get_packages(
    endpoint_list, "testing", "extra", "x86_64", config.get_access_token()
)
formdata = []
if len(pkgs) > 0:
    for pkg in pkgs:
        formdata.append({"name": pkg["name"], "section": from_section})
        print(f"{pkg['name']} ", end="")
else:
    print("no packages found")
    exit(0)
print()
print(
    f"Removing {len(formdata)} packages from {from_section['branch']}/{from_section["repository"]}/{from_section['architecture']}"
)
json_formdata = json.dumps(formdata)
files = {("to_delete", (None, json_formdata, "application/json"))}

headers = {
    "User-Agent": config.user_agent,
    "Authorization": f"Bearer {config.get_access_token()}",
    "X-BxtCtl-Request-Id": str(uuid.uuid4()),
}

session = requests.Session()
request = Request("POST", endpoint_rm, headers=headers, files=files)
token = config.get_access_token()
req = request.prepare()

print("bxt_delete_pkg: BearerAuth")
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
