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
import datetime
import json
import time
import uuid

import requests
from bxtctl.Bxt.BxtConfig import BxtConfig
from requests import Request
from requests import RequestException

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


# endpoint
endpoint = f"{config.get_url()}/{config.endpoint["pkgCommit"]}"
# the path is provided when executing the path in the CLI
to_section = {
    "branch": "testing",
    "repository": "extra",
    "architecture": "x86_64",
}
# workspace with $branch/$repo/$arch
# workspace = f"{config.workspace}/testing/extra/aarch64"
workspace = f"{config.get_workspace()}/testing/extra/x86_64"
# dummies
pkgver = "20240930.1011"
dummy1 = f"a-dummy1-{pkgver}-1-any.pkg.tar.zst"
dummy2 = f"a-dummy2-{pkgver}-1-any.pkg.tar.zst"
dummy3 = f"a-dummy3-{pkgver}-1-any.pkg.tar.zst"
# files
files = {
    (
        "package1",
        (dummy1, open(f"{workspace}/{dummy1}", "rb"), "application/octet-stream"),
    ),
    (
        "package1.signature",
        (
            f"{dummy1}.sig",
            open(f"{workspace}/{dummy1}.sig", "rb"),
            "application/octet-stream",
        ),
    ),
    ("package1.section", (None, json.dumps(to_section), "application/json")),
    (
        "package2",
        (dummy2, open(f"{workspace}/{dummy2}", "rb"), "application/octet-stream"),
    ),
    (
        "package2.signature",
        (
            f"{dummy2}.sig",
            open(f"{workspace}/{dummy2}.sig", "rb"),
            "application/octet-stream",
        ),
    ),
    ("package2.section", (None, json.dumps(to_section), "application/json")),
    (
        "package3",
        (dummy3, open(f"{workspace}/{dummy3}", "rb"), "application/octet-stream"),
    ),
    (
        "package3.signature",
        (
            f"{dummy3}.sig",
            open(f"{workspace}/{dummy3}.sig", "rb"),
            "application/octet-stream",
        ),
    ),
    ("package3.section", (None, json.dumps(to_section), "application/json")),
}
# headers
headers = {
    "User-Agent": config.user_agent,
    "Authorization": f"Bearer {config.get_access_token()}",
    "X-BxtCtl-Request-Id": str(uuid.uuid4()),
}
# create session object
session = requests.Session()
# populate request with endpoint data and headers
request = Request("POST", endpoint, headers=headers, files=files)
token = config.get_access_token()
# prepare request
req = request.prepare()
# print some info about the request
print("bxt_upload_pkg: BearerAuth")
# copy headers to separate object to obscure the token data string
to_be_printed = req.headers.copy()
to_be_printed["Authorization"] = f"Bearer {token[:15]}...{token[-15:]}"
print(f"req headers   : {to_be_printed}")
print(f"req url       : {req.url}")
print(f"req body      : {req.body}")
print("--------------------------------------------------------------")
print("request begin    --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
logstart = datetime.datetime.now()
try:

    response = session.send(req, timeout=30)

except RequestException as e:
    # no response fro service
    print("RequestException --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
    print(e)
    exit(1)
except (Exception,) as e:
    print("Exception --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
    print(e)
    exit(1)

print("response recv    --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
print("response headers --> ", response.headers)
print("response status  --> ", response.status_code)
print("response content --> ", response.content)
