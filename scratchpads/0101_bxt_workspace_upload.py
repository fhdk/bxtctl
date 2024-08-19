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

from requests_toolbelt import MultipartEncoder

from Bxt.BxtAcl import BxtAcl
from Bxt.BxtConfig import BxtConfig
from Bxt.BxtFile import BxtFile
from Bxt.BxtSession import BxtSession
from Bxt.BxtWorkspace import BxtWorkspace
from Bxt.Utils import path_completion, encode_package_data

"""
This file is to test the correct creating of a workspace
The workspace must populated with a folder tree matching the permissions
"""
config = BxtConfig()

if not config.valid_config():
    y = config.configure()

if not config.get_access_token():
    z = config.login()

# initialize a session object
bxt_session = BxtSession(BxtConfig.user_agent)
sections = bxt_session.get_sections(
    f"{config.get_url()}/{BxtConfig.endpoint['pkgSection']}",
    config.get_access_token(),
)

acl = BxtAcl(sections)

config.repos = path_completion(acl.get_branches, acl.get_repositories, acl.get_architectures)

print(config.workspace)
print(config.repos)

ws = BxtWorkspace(config.workspace, config.repos)
files = ws.get_packages("testing/extra/x86_64")

# PoC create form with multiple packages for uploading in one request
form_data = MultipartEncoder(fields={})
# placeholder for fields
encodings = {}
for idx, file in enumerate(files):
    # use a function to return the fields for the package
    # remember to increment index to create unique form references
    encoded = encode_package_data(file, idx + 1)
    # add the encoded element to the placeholder
    encodings.update(encoded)

# encode the fields to a multipart/form-data
form_data = MultipartEncoder(fields=encodings)
print(form_data)
print(form_data.content_type)
print(form_data.to_string())
