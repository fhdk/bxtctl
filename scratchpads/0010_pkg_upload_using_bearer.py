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
from pprint import pprint

import requests
from Bxt.BxtConfig import BxtConfig
from requests import Request
from requests import RequestException
from requests_toolbelt.multipart.encoder import MultipartEncoder

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
workspace = f"{config.workspace}/testing/extra/x86_64"
test_pkg_1 = "a-dummy1-0-0-any.pkg.tar.zst"
test_pkg_2 = "a-dummy2-0-0-any.pkg.tar.zst"

# internal note: formdata can be either a tuple or a dictionary
#  tuple preserves the order the elements
#  dictionary posts the data in arbitrary order
# form_data = (
#     ("package1", (test_pkg_1, open(f"{test_repo}/{test_pkg_1}", "rb"))),
#     ("package1.signature",
#      (f"{test_pkg_1}.sig", open(f"{test_repo}/{test_pkg_1}.sig", "rb"))),
#     ("package1.section", (None, json.dumps(to_section))),
# )
bxt_token = str(uuid.uuid4())
boundary = f"------{bxt_token}"
multipart_data = MultipartEncoder(
    boundary=boundary,
    fields=(
        ("package1", (test_pkg_1, open(f"{workspace}/{test_pkg_1}", "rb"), "application/octet-stream")),
        ("package1.signature", (f"{test_pkg_1}.sig", open(f"{workspace}/{test_pkg_1}.sig", "rb"), "application/octet-stream")),
        ("package1.section", (json.dumps(to_section), "application/json")),
    )
)

# headers
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0",
    "Authorization": f"Bearer {config.get_access_token()}",
    "Content-Type": "multipart/form-data; boundary=" + boundary,
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "x-bxtctl-token": bxt_token,
    "Connection": "keep-alive",
}
# create session object
session = requests.Session()
# populate request with endpoint data and headers
request = Request('post', endpoint, headers=headers, data=multipart_data)

# prepare request
req = request.prepare()
# print some info about the request
print("bxt_upload_pkg: BearerAuth")
# copy headers to separate object to obscure the token data string
header_to_print = headers
header_to_print["Authorization"] = f"Bearer {config.get_access_token()[:15]}...{config.get_access_token()[-15:]}"
print(f"req headers   : {headers}")
print(f"req url       : {req.url}")
print("Content-Length: ", req.headers["Content-Length"])
print(multipart_data.to_string())

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
