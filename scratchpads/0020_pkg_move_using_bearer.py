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
from requests import Request
from requests import RequestException
from Bxt.BxtConfig import BxtConfig
from requests_toolbelt.multipart.encoder import MultipartEncoder

"""
part two of four in a series of scratchpads
moves the test packages

For now the result is verified by using the WebUI
A later update will use the packages list endpoint 
to verify the package moved to the target repo 
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

form_content = json.dumps(
    [{"name": dummy1, "from_section": from_section, "to_section": to_section},
     {"name": dummy2, "from_section": from_section, "to_section": to_section}])

# formdata can be either a tuple or a dictionary
# tuple preserves the order the elements
# dictionary posts the data in arbitrary order
multipart_data = MultipartEncoder(
    fields={
        ("to_move", form_content)
    }
)
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
    "Content-Type": multipart_data.content_type
}

session = requests.Session()
request = Request('POST', endpoint, data=multipart_data, headers=headers)

req = request.prepare()

print("bxt_move_pkg  : BearerAuth")
headers["Authorization"] = f"Bearer {token[:15]}...{token[-15:]}"
print(f"req headers   : {headers}")
print(f"req url       : {req.url}")
print(f"form data     : {req.body}")
print(f"multipart_data: {multipart_data.to_string()}")

try:
    response = session.send(req, stream=True)
    print("response recv    --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("response headers --> ", response.headers)
    print("response status  --> ", response.status_code)
    print("response content --> ", response.content)
except RequestException as e:
    print("response recv    --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
    print(e)
