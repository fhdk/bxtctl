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

import time
from bxtctl.Bxt.BxtConfig import BxtConfig
from bxtctl.Bxt.BxtSession import BxtSession
import logging

"""
Get a list of packages from 
from: stable -> extra -> x86_64 repo
"""
logging.basicConfig(level=logging.DEBUG)

config = BxtConfig()

if not config.valid_config():
    y = config.configure()

if not config.get_access_token():
    z = config.login()

if config.valid_token():
    if not config.renew_access_token():
        z = config.login()

token = config.get_access_token()
endpoint = f"{config.get_url()}/{config.endpoint["pkgLog"]}"
http = BxtSession(config.user_agent)
params = {
    "since": "2024-08-28T00:00:00.0Z",
    "until": "2024-09-04T00:00:00.0Z",
    "text": "dummy",
}
print("bxt_get_logs : ")
print("log request begin --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
pkgs = http.get_logs(endpoint, params, config.get_access_token())
for pkg in pkgs:
    print(f"source: {pkg}")
