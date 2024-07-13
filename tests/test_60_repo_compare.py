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
from Bxt.Http import Http
import jwt
from pprint import pprint
import os

"""
Get a list of packages from 
from: stable -> extra -> x86_64 repo
"""

config = BxtConfig()

if not config.is_valid():
    y = config.configure()

if not config.get_access_token():
    z = config.login()

if config.is_token_expired():
    if not config.renew_access_token():
        z = config.login()

token = config.get_access_token()
endpoint = f"{config.get_url()}/{config.endpoint["pkgList"]}"
http = Http(config.user_agent, config.get_access_token())

print("bxt_compare : ")
print("compare request begin    --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
compare_data = [{"branch": "unstable", "repository": "core", "architecture": "x86_64"},
                {"branch": "testing", "repository": "core", "architecture": "x86_64"},
                ]
comparison = http.compare(endpoint, compare_data)
print("compare request response --> ", time.strftime("%Y-%m-%d %H:%M:%S"))

pprint(f"{comparison}")

print("compare response parsed  --> ", time.strftime("%Y-%m-%d %H:%M:%S"))
